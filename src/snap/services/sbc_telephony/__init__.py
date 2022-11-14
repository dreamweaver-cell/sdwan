"""Define the SBC-telephony service
Example:
"services":
    "sbc_telephony": {
        "vpn800_static_nat_source_ip": "192.0.2.20",        // optional variable
        "vpn800_static_nat_translate_ip": "213.249.52.83",  // only needed if vpn800 (SBC)
        "interfaces": [
            "GigabitEthernet0/0/0.801",
            "GigabitEthernet0/0/0.101"
        ],
        "enabled": true
    }
"interfaces": {
    "GigabitEthernet0/0/0.101": {
        "description": "** SBC_telephony **",
        "helper_address": [                             // Helper addresses are optional
            "10.61.95.125",
            "10.61.95.126"
        ],
        "ipv4": "10.186.23.2/24",
        "standby": "10.186.23.1"
    } }
"""
from snap.service import Service


class ServiceSbcTelephony(Service):
    """Define head service"""

    name = "sbc_telephony"
    provision_order = 201

    def service_logic(self, device_variables: dict, device_template: dict):
        """Function called before updateing templates. All service logic goes here."""
        myvars = device_variables['services'][self.name]
        device_variables['vpn800_enabled'] = myvars.get('vpn800_static_nat_translate_ip')

    def update_device_template(self, device_vars: dict, device_template: dict) -> dict:
        """Update device template."""
        self.template = self._render_template_file(device_vars)
        return self.merge_generalTemplates(self.template, device_template)
