"""Define the Zscaler-service with GRE-tunnels."""
from snap.service import Service


class ServiceZscaler(Service):
    """Define head service"""

    name = "zscaler"
    provision_order = 25

    def service_logic(self, device_variables: dict, device_template: dict):
        """Function called before updateing templates. All service logic goes here."""

    def update_device_template(self, device_conf: dict, device_template: dict) -> dict:
        """update device template with Zscaler."""
        self.template = self._render_template_file(device_conf)
        return self.merge_generalTemplates(self.template, device_template)

    def validate_service(self):
        """Tests service"""
        pass
