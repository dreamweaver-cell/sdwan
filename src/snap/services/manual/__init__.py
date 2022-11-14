"""
Define the Manual override service.
Will overwrite the devicetemplate with the file given
Limitations:
- only support to completely overwrite the devicetemplate.

Example:
"manual": {
    "device_template": {
        "filename": "sesthxx3rtr001_template.json"
    },
    "variables": {
        "parent_lan_if_name": "GigabitEthernet0/7/1"
    },
    "enabled": true
}

"""
import json

from jinja2 import Template

from snap.config import SNAPCONF_DIR
from snap.logger import log
from snap.service import Service


class ServiceManual(Service):
    """Define manual-service."""

    name = "manual"
    provision_order = 999  # must be last
    hostname = ""

    def service_logic(self, device_variables: dict, device_template: dict):
        log.debug("%s updateing variables", self.name)
        srv_config = device_variables['services'][self.name]
        device_variables.update(srv_config['variables'])

        if template_config := srv_config.get('device_template', {}):
            if filename := template_config.get('filename', ""):
                # Completely overwrite device template when filename.
                log.debug("%s replace template", self.name)
                template_dir = f"{SNAPCONF_DIR}/device_templates"
                with open(f"{template_dir}/{filename}", mode="r", encoding="utf-8") as temp:
                    text = Template(temp.read())
                    renered = text.render(device_variables)
                    self.template = json.loads(renered)
                return self.template
            else:
                log.info("%s no devicetemplate config.", self.name)

    def update_device_template(self, device_conf: dict, device_template: dict) -> dict:
        """replace the device template with this template."""
        device_template.clear()
        device_template.update(self.template)
        return device_template

    def validate_service(self):
        """Tests service"""
