import json
import os
import sys
from pathlib import Path
from typing import Optional

import click
import yaml
from deepdiff import DeepDiff
from vmanage.api.authentication import Authentication
from vmanage.api.device import Device as Vdevice
from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods
from vmanage.data.template_data import TemplateData

import snap.config as conf
import snap.services  # noqa: F401
from snap.json_validate import json_validate
from snap.logger import log
from snap.service import Service
from snap.utils import get_inputdata_vars, get_vardiff
from snap.viptela import SnapDeviceTemplates


class Device(Vdevice):
    """
    Manages SDWAN-devices.
    Args:

        services (list of strings): list of service names
        device_template (dict): the device template
        device_variables (dict): variables used by template
    """

    def __init__(self, hostname: str = ''):
        """Initialize device class."""

        self.device_template: dict = {}
        self.device_variables: dict = {}
        self.services = ["head", "base"]
        self._auth = None
        self._snapfilename = ''
        self.hostname = hostname

    @property
    def hostname(self) -> str:
        return self._hostname

    @hostname.setter
    def hostname(self, name: str):
        self._hostname = name
        self._snapfilename = f"{conf.SNAPCONF_DIR}/{name}.json"

    @property
    def snapfilename(self) -> str:
        return self._snapfilename

    @property
    def uuid(self) -> str:
        return f"{self.device_variables['part_number']}-{ self.device_variables['crypto_sn']}"

    def _vinit(self):
        if not self._auth:
            self._auth = Authentication(host=conf.VMANAGE_HOST,
                                        user=conf.TACACS_USERNAME,
                                        password=conf.TACACS_PASSWORD).login()
            super(Device, self).__init__(self._auth, conf.VMANAGE_HOST)

    @staticmethod
    def get_devicetemplate_filename(hostname: str) -> str:
        return f"{conf.ANSIBLE_FILES}/{hostname}.json"

    @staticmethod
    def get_variable_filename(hostname: str) -> str:
        directory = f"{conf.ANSIBLE_INVENTORY}/host_vars/{hostname}"
        return f"{directory}/{hostname}.yml"

    def get_device_uuid(self, uuid: str) -> dict:
        """Find device in vmanage

        Returns:
            result (dict): All data associated with a response.
        """

        url = f"{self.base_url}system/device/vedges?uuid={uuid}"
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def read_config_from_file(self, snapconfig_file: str = '', hostname: str = ''):
        """Read configurationfile named <hostname>.json in provided directory.
        Validates json against jsonschema and pass over to provisioning.
        """
        if not snapconfig_file:
            self.hostname = hostname
        else:
            self._snapfilename = snapconfig_file
        with open(self._snapfilename, encoding="utf-8") as host_configuration_file:
            self._device_config = json.load(host_configuration_file)

        self.hostname = self._device_config["device_name"]

        # removing the services that not are defined from list and sort it in provisioning order
        for s in self._device_config["services"].keys():
            if s in Service.get_services():
                self.services.append(s)
        self.services = sorted(self.services, key=lambda x: Service(x).provision_order)
        json_validate(self._device_config, conf.JSON_DEVICE_CONFIG_SCHEMA)
        self.device_variables = self._device_config.copy()

    def read_config_from_vmanage(self, hostname: str):
        """Read devicetemplate and variables from vmanage named."""
        pass

    def validate_devicetemplate(self):
        json_validate(self.device_template, conf.JSON_DEVICE_TEMPLATE)

    def write_device_template(self, filename: str = ""):
        """write the device_template to disk"""
        filename = self.get_devicetemplate_filename(self.device_variables["device_name"])
        with open(filename, "w", encoding="utf-8") as filen:
            json.dump(self.device_template, filen, indent=4)

    def write_variables_file(self):
        """write device_vars- file in ansible-format (host_vars) to disk"""
        sdwan = {"sdwan": self.device_variables}
        filename = self.get_variable_filename(self.device_variables["device_name"])
        Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as filen:
            yaml.dump(sdwan, filen)

    def provision_services(self):
        for srv in [Service(name) for name in self.services if Service(name)]:
            log.info("service: %s", srv.name)
            srv.service_logic(self.device_variables, self.device_template)
            srv.update_device_variables(self.device_variables)
            srv.update_device_template(self.device_variables, self.device_template)
        log.debug(json.dumps(self.device_template))

    def load_snapfile(self, filename: str):
        """Read snap-configfile and provision all services."""
        self.read_config_from_file(snapconfig_file=filename)
        self.provision_services()
        self.validate_devicetemplate()

    def find_generaltemplate(self, templatename: str) -> Optional[str]:
        """find templatesnippet in generaltemplates"""
        mydict = [
            d for d in self.device_template['generalTemplates']
            if d['templateName'] == templatename
        ]
        return mydict[0] if len(mydict) else None

    def delete_from_generaltemplates(self, templatename: str = "") -> dict:
        """deletes a template (and subtemplates) with templateName from generaltemplates"""
        gt = self.device_template['generalTemplates']
        new = [i for i in gt if not i['templateName'] == templatename]
        self.device_template['generalTemplates'] = new
        return self.device_template

    def print_device_template(self):
        click.echo(json.dumps(self.device_template, indent=4))

    def print_device_variables(self):
        click.echo(json.dumps(self.device_variables, indent=4))

    def write_template_files(self):
        self.write_device_template()
        self.write_variables_file()

    def diff_config(self, diffile: str) -> list:
        """compare configs"""
        attached = {}

        if diffile == "vmanage":
            templatename = self.device_template['templateName']
            self._vinit()
            td = TemplateData(self._auth, conf.VMANAGE_HOST)
            dt = SnapDeviceTemplates(self._auth, conf.VMANAGE_HOST)

            vtemplate = td.export_device_template_list(factory_default=True,
                                                       name_list=templatename)[0]
            devcomp = vtemplate.copy()
            for key in conf.DIFF_DEV_IGNORE:
                devcomp.pop(key, None)
            devcomp['connectionPreference'] = True
            devcomp['connectionPreferenceRequired'] = True
            devcomp['templateId'] = ""

            attached = dt.get_template_input(template_id=vtemplate['templateId'],
                                             device_id_list=[self.uuid])
        else:
            with open(diffile, encoding="utf-8") as fp:
                devcomp = json.load(fp)

        ddiff = DeepDiff(devcomp, self.device_template, ignore_order=True)
        return_diff = []
        if ddiff:
            #print("--- There are changes in device template ---")
            # pprint(ddiff, compact=False)
            return_diff.append(ddiff)

        if attached.get('data'):
            old = get_inputdata_vars(attached)
            new = self.device_variables
            diff = get_vardiff(old=old, new=new)
            if diff:
                return_diff.append(diff)
        return return_diff

    @staticmethod
    def print_diff(diff: list):
        """Print out result of diff-action."""
        if diff:
            print("---- Device template diff ---")
            print(diff[0])
            if len(diff) > 1:
                print("---- Variables diff ---")
                print(diff[1])
        else:
            print("---- No change in device template/variables ----")

    def in_vmanage(self) -> bool:
        self._vinit()
        data = self.get_device_uuid(self.uuid)
        if data and 'uuid' in data[0]:
            return True
        return False

    def vmanage_attach(self) -> str:
        """Attaching the device-template in vmanage using variables."""
        if not self.in_vmanage():
            log.error("Device not defined in vmanage")
            sys.exit()

        self._vinit()
        dt = SnapDeviceTemplates(self.session, conf.VMANAGE_HOST)
        # Find template_id.. have to be pushed first
        template_name = self.device_template['templateName']
        vtemplate = [t for t in dt.get_device_templates() if t['templateName'] == template_name]
        try:
            template_id = vtemplate[0]['templateId']
        except IndexError:
            log.error("DeviceTemplate not found in Vmanage.")

        # --- Fixa till variables
        variables = {}
        variables['host_name'] = self.device_variables['device_name']
        variables['system_ip'] = self.device_variables['system_ip']
        variables['site_id'] = self.device_variables['site_id']
        # --- Fix för att fel variable namn parsas ut...
        # self.device_variables['Kbps'] = self.device_variables['internet_shaping_rate']

        variables['variables'] = self.device_variables

        uuid = {self.uuid: variables}

        response = dt.attach_to_template(template_id, config_type="template", uuid=uuid)
        action_id = response.get("action_id", "No ID!")
        action_status = response.get("action_status")
        if not (action_status == "success" or action_status == "success_scheduled"):
            raise Exception("Attach to vmanage failed!")
        log.info("Attach done: %s", action_id)
        return action_id
