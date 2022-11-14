"""Define the Header-service"""

# import snap.config as conf
from snap.logger import log
from snap.service import Service


class Serviceoffice_ds_switch_ospfv3(Service):
    """vlan 11 is used as a Office Facility network."""

    name = "office_ds_switch_ospfv3"
    provision_order = 326

    def service_logic(self, device_variables: dict, device_template: dict):
        """Function called before updateing templates. All service logic goes here."""
        log.warning(
            "OSPF is configured. Please check 'mtu-ignore' and 'capability vrf-lite' on switch!")

    def update_device_template(self, device_conf: dict, device_template: dict) -> dict:
        """update device template with office_ds_switch_ospfv3."""
        self.template = self._render_template_file(device_conf)
        return self.merge_generalTemplates(self.template, device_template)
