"""Define the Header-service"""
from snap.service import Service


class Servicecapwap(Service):
    """Define head service"""

    name = "capwap"
    provision_order = 151

    def service_logic(self, device_variables: dict, device_template: dict):
        """Function called before updateing templates. All service logic goes here."""

        # set capwap services

    def update_device_template(self, device_conf: dict, device_template: dict) -> dict:
        """update device template with capwap."""
        self.template = self._render_template_file(device_conf)
        return self.merge_generalTemplates(self.template, device_template)

    def validate_service(self):
        """Tests service"""
        pass
