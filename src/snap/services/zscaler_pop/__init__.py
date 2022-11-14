"""Define the Header-service"""

# import snap.config as conf
from snap.service import Service


class ServiceZscaler_pop(Service):
    """vlan 80 is used as a Office Facility network."""

    name = "zscaler_pop"
    provision_order = 205

    def service_logic(self, device_variables: dict, device_template: dict):
        """Function called before updateing templates. All service logic goes here."""

    def update_device_template(self, device_conf: dict, device_template: dict) -> dict:
        """update device template with Office Compute."""
        self.template = self._render_template_file(device_conf)
        return self.merge_generalTemplates(self.template, device_template)
