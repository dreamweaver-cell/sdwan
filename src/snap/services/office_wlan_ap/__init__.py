"""Define the Header-service"""

# import snap.config as conf
from snap.service import Service


class Servicevlan332_external_partners(Service):
    """vlan 332 is used as a partner access."""

    name = "vlan332_external_partners"
    provision_order = 222

    def service_logic(self, device_variables: dict, device_template: dict):
        """Function called before updateing templates. All service logic goes here."""

    def update_device_template(self, device_conf: dict, device_template: dict) -> dict:
        """update device template with Office Facility."""
        self.template = self._render_template_file(device_conf)
        return self.merge_generalTemplates(self.template, device_template)
