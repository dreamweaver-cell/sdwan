"""Define the Header-service"""

# import snap.config as conf
from snap.service import Service


class Serviceoffice_printer(Service):
    """vlan 11 is used as a Office Facility network."""

    name = "office_printer"
    provision_order = 220

    def service_logic(self, device_variables: dict, device_template: dict):
        """Function called before updateing templates. All service logic goes here."""

    def update_device_template(self, device_conf: dict, device_template: dict) -> dict:
        """update device template with Office Office Printer."""
        self.template = self._render_template_file(device_conf)
        return self.merge_generalTemplates(self.template, device_template)
