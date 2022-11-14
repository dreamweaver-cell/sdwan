"""Define the Header-service"""
from os import stat
from typing import Tuple

import yaml
from hmnet import netdb

import snap.config as conf
from snap.service import Service
from snap.viptela_types import get_device_type


class ServiceHead(Service):
    """Define head service"""

    name = "head"
    provision_order = 1

    @staticmethod
    def get_siteid(device_variables: dict) -> str:
        """Checkout existing or register new site."""

        s = netdb.Site(device_variables["device_name"])
        device_variables["site_id"] = s.siteid
        device_variables["region"] = s.region
        return s.siteid

    def get_systemip(self, device_variables: dict) -> str:
        ip = device_variables["interfaces"]["Loopback5"]["ipv4"]
        ip = ip.split("/")[0]
        return ip

    def get_region_variables(self, device_variables: dict) -> Tuple:
        """Get region specific variables."""
        with open(f"{conf.snapdir}/regionalvar.yml") as file:
            regional_vars = yaml.load(file, Loader=yaml.FullLoader)
        return regional_vars[device_variables["region"]]

    def update_device_variables(self, device_variables: dict) -> dict:
        """updates device variables, ONLY if they dont already exists"""
        filename = "variables.j2"
        template = self._read_template_file(filename)
        if template:
            variables = self._render_template_file(device_variables, "variables.j2")
            for k, v in variables.items():
                if k not in device_variables:
                    device_variables[k] = v
            return device_variables

    def service_logic(self, device_variables: dict, device_template: dict):
        """Set variables used when provisioning services.

        Attributes:
            system_ip (str): The system ip used when communicating to device name
            snmp_device_location: (str): SNMP location, takes first 5 digits in hostname
            internet_if_ipv4_address (str): Set internet ipv4 address
            lan_if_name (str): If the device is a C1111 we use vlan2 as default,
                               if 4K use the physical address.
        """

        device_variables["viptela_type"] = get_device_type(device_variables["part_number"])
        device_variables["system_ip"] = self.get_systemip(device_variables)
        self.get_siteid(device_variables)
        device_variables.update(self.get_region_variables(device_variables))

        device_variables["crypto_sn"] = device_variables["device_serial_number"]

        # Craft snmp_device_location
        device_variables["snmp_device_location"] = device_variables["device_name"][0:5]

        # Set Internet ipv4 address if existing
        try:
            device_variables["internet_if_ipv4_address"] = device_variables["interfaces"][
                device_variables["services"]["internet"]["interfaces"][0]]["ipv4"]
        except KeyError:
            pass

        # Set LAN interface
        for lan_interface in device_variables["services"]["lan"]["interfaces"]:
            if "Ethernet" in lan_interface:
                try:
                    # vlan_tag = lan_interface.split(".")[1]
                    device_variables["lan_if_name"] = lan_interface.split(".")[0]
                except IndexError:
                    pass

    def validate_service(self):
        """Tests service"""
