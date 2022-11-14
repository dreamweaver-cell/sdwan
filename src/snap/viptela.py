import json
import re
import time

from vmanage.api.authentication import Authentication
from vmanage.api.device_templates import DeviceTemplates
from vmanage.api.feature_templates import FeatureTemplates
from vmanage.api.http_methods import HttpMethods
from vmanage.api.utilities import Utilities
from vmanage.data.parse_methods import ParseMethods

import snap.config as conf
from snap.logger import log


class SnapUtilities(Utilities):
    """SNAP Utilities class."""

    def waitfor_action_completion(self, action_id: str) -> dict:
        status = 'in_progress'
        response = {}
        action_status = None
        action_activity = None
        action_config = None
        log.debug(f"polling: {self.base_url}device/action/status/{action_id}")
        actions_printed = 0
        while status == "in_progress":
            url = f"{self.base_url}device/action/status/{action_id}"
            response = HttpMethods(self.session, url).request('GET')
            ParseMethods.parse_data(response)

            if 'json' in response:
                status = response['json']['summary']['status']
                log.debug(f"STATUS: {status}")
                if 'data' in response['json'] and response['json']['data']:
                    # log.debug(f"DATA: {response['json']['data'][0]}")
                    action_status = response['json']['data'][0]['statusId']
                    action_activity = response['json']['data'][0]['activity']
                    if action_activity:
                        for _ in range(actions_printed, len(action_activity)):
                            log.info(action_activity[_])
                        actions_printed = len(action_activity)
                    if 'actionConfig' in response['json']['data'][0]:
                        action_config = response['json']['data'][0]['actionConfig']
                    else:
                        action_config = None
                else:
                    action_status = status
            else:
                raise Exception(msg="Unable to get action status: No response")
            time.sleep(10)

        return {
            'action_response': response['json'],
            'action_id': action_id,
            'action_status': action_status,
            'action_activity': action_activity,
            'action_config': action_config
        }


class SnapDeviceTemplates(DeviceTemplates):
    """SNAP devicetemplate class."""

    def get_template_input(self, template_id: str, device_id_list: list = None) -> dict:
        """Get the input associated with a device attachment.

        Args:
            template_id (string): Template ID
            device_id_list (list): list of device UUID's to get input for

        Returns:
            result (dict): All data associated with a response.

        """

        if device_id_list:
            deviceIds = device_id_list
        else:
            deviceIds = []
        payload = {
            "deviceIds": deviceIds,
            "isEdited": False,
            "isMasterEdited": False,
            "templateId": template_id
        }
        return_dict: dict = {"columns": [], "data": []}

        url = f"{self.base_url}template/device/config/input"
        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))

        if 'json' in response:
            if 'header' in response['json'] and 'columns' in response['json']['header']:
                column_list = response['json']['header']['columns']

                regex = re.compile(r'\((?P<variable>[^(]+)\)$')

                for column in column_list:
                    if column['editable']:
                        match = regex.search(column['title'])
                        if match:
                            variable = match.groups('variable')[0]
                        else:
                            # If the variable is not found, use toolTip as variable name
                            variable = column.get("toolTip")

                        entry = {
                            'title': column['title'],
                            'property': column['property'],
                            'variable': variable
                        }
                        return_dict['columns'].append(entry)
            if 'data' in response['json'] and response['json']['data']:
                return_dict['data'] = response['json']['data']

        return return_dict

    def attach_to_template(self, template_id: str, config_type: str, uuid: dict) -> str:
        """SNAP - Attach and device to a template

        Args:
            template_id (str): The template ID to attach to
            config_type (str): Type of template i.e. device or CLI template
            uuid (dict): The UUIDs of the device to attach and mapping for corresponding variables,
            system-ip, host-name

        Returns:
            action_id (str): Returns the action id of the attachment

        """
        # Construct the variable payload

        device_template_var_list = list()
        template_variables = self.get_template_input(template_id)

        for device_uuid in uuid:

            device_template_variables = {
                "csv-status": "complete",
                "csv-deviceId": device_uuid,
                "csv-deviceIP": uuid[device_uuid]['system_ip'],
                "csv-host-name": uuid[device_uuid]['host_name'],
                '//system/host-name': uuid[device_uuid]['host_name'],
                '//system/system-ip': uuid[device_uuid]['system_ip'],
                '//system/site-id': uuid[device_uuid]['site_id'],
            }

            # Make sure they passed in the required variables and map
            # variable name -> property mapping

            for entry in template_variables['columns']:
                if entry['variable']:
                    if entry['variable'] in uuid[device_uuid]['variables']:
                        device_template_variables[
                            entry['property']] = uuid[device_uuid]['variables'][entry['variable']]
                    else:
                        raise RuntimeError(
                            f"{entry['variable']} is missing for template {uuid[device_uuid]['host_name']}"  # noqa
                        )

            device_template_var_list.append(device_template_variables)

        payload = {
            "deviceTemplateList": [{
                "templateId": template_id,
                "device": device_template_var_list,
                "isEdited": False,
                "isMasterEdited": False
            }]
        }

        if config_type == 'file':
            url = f"{self.base_url}template/device/config/attachcli"
        elif config_type == 'template':
            url = f"{self.base_url}template/device/config/attachfeature"
        else:
            raise RuntimeError('Got invalid Config Type')

        utils = SnapUtilities(self.session, self.host, self.port)
        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
        action_id = ParseMethods.parse_id(response)
        response = utils.waitfor_action_completion(action_id)
        return response


class SnapFeatureTemplates(FeatureTemplates):
    """SNAP override class."""

    def __init__(self):
        self._auth = Authentication(host=conf.VMANAGE_HOST,
                                    user=conf.TACACS_USERNAME,
                                    password=conf.TACACS_PASSWORD).login()
        super().__init__(self._auth, conf.VMANAGE_HOST)
