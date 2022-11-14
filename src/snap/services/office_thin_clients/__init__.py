"""Define the Header-service"""
from snap.service import Service


class Serviceoffice_thin_clients(Service):
    """Define head service"""

    name = "office_thin_clients"
    provision_order = 153

    def service_logic(self, device_variables, device_template):
        """Function called before updateing templates. All service logic goes here."""

        # set office_thin_clients services

    def update_device_template(self, device_conf, device_template) -> dict:
        """update device template with office_thin_clients."""
        self.template = self._render_template_file(device_conf)
        return self.merge_generalTemplates(self.template, device_template)

    def validate_service(self):
        """Tests service"""
        pass
