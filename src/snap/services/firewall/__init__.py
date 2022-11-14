"""Define the Header-service"""
from snap.service import Service


class ServiceFirewall(Service):
    """Define head service"""

    name = "firewall"
    provision_order = 150

    def service_logic(self, device_variables: dict, device_template: dict):
        """Function called before updateing templates. All service logic goes here."""

        # set firewall services

    def update_device_template(self, device_conf: dict, device_template: dict) -> dict:
        """update device template with VPLS."""
        self.template = self._render_template_file(device_conf)
        return self.merge_generalTemplates(self.template, device_template)

    def validate_service(self):
        """Tests service"""
        pass
