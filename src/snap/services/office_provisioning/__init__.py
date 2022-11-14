"""Define the Header-service
Example:
"services":
    "office_provisioning": {
        "interfaces": [
            "GigabitEthernet0/0/0.1",
            "GigabitEthernet0/0/0.1"
        ],
        "enabled": true
    }
"interfaces": {
    "GigabitEthernet0/0/0.1": {
        "description": "** Office Provisioning **",
        "ipv4": "x.x.x.x/yy",
        "standby": "x.x.x.x/yy"
    } }
"""

# import snap.config as conf
from snap.service import Service


class Serviceoffice_provisioning(Service):
    """vlan 1 is used as a Office Facility network."""

    name = "office_provisioning"
    provision_order = 300

    def service_logic(self, device_variables: dict, device_template: dict):
        """Function called before updateing templates. All service logic goes here."""

    def update_device_template(self, device_conf: dict, device_template: dict) -> dict:
        """update device template with Office Office provisioning."""
        self.template = self._render_template_file(device_conf)
        return self.merge_generalTemplates(self.template, device_template)
