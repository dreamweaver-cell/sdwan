"""Define the Base-service"""
from snap.service import Service


class ServiceBase(Service):
    """Define base service"""

    name = "base"
    provision_order = 2

    def service_logic(self, device_variables: dict, device_template: dict):
        device_variables["lo5_ipv4_address"] = f"{device_variables['system_ip']}/32"

        general_templates = device_template["generalTemplates"]
        if "ISR4" in device_variables["part_number"]:
            general_templates.append({
                "templateName":
                    "ISR4K_VPN_512_Template",
                "templateType":
                    "cisco_vpn",
                "subTemplates": [{
                    "templateName": "PROD-VPN512-ISR4K",
                    "templateType": "cisco_vpn_interface",
                }],
            })
        else:
            general_templates.append({
                "templateName": "Factory_Default_Cisco_VPN_512_Template",
                "templateType": "cisco_vpn",
            })

        if "C1111-8P" in device_variables["part_number"]:
            general_templates.append({
                "templateName": "PROD-EDGE-SWITCHPORT",
                "templateType": "switchport"
            })

    def validate_service(self):
        """Tests service"""
        pass
