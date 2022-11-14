"""Define Internet service"""

# import snap.config as conf

from typing import Literal, Optional

from snap.logger import log
from snap.service import Service


class Serviceinternet(Service):
    """Define the service class."""

    name = "internet"
    provision_order = 13

    def get_vpn0_gw(self, device_variables: dict, internet_interface: str) -> Optional[str]:
        # Handle DHCP på wan-if
        for route in device_variables["routing"]["static"]:
            if route["vrf"] == "vpn0" and route["nexthop_if"] == internet_interface \
                    or "INTERNET" in route["vrf"] and route["nexthop_if"] == internet_interface:
                return route["nexthop_ip"]
        return None

    def service_logic(self, device_variables: dict, device_template: dict):
        """Function called before updateing templates. All service logic goes here."""
        circuit_nr = 0
        circuit_index = 1
        for internet_circuit_name in device_variables["services"]["internet"]["interfaces"]:
            if circuit_nr == 0:
                circuit_index = ""

            inet_ifname = str(internet_circuit_name)
            inet_if = device_variables["interfaces"][inet_ifname]
            device_variables["dhcp_for_vpn0"] = "dhcp" in inet_if["ipv4"] or None  # noqa: E501
            device_variables[f"internet{circuit_index}_if_name"] = str(inet_ifname)
            device_variables[f"internet{circuit_index}_if_ipv4_address"] = device_variables[
                "interfaces"][inet_ifname]["ipv4"]  # noqa: E501
            device_variables[f"internet{circuit_index}_if_description"] = device_variables[
                "interfaces"][inet_ifname]["description"]  # noqa: E501
            device_variables[f"internet{circuit_index}_shaping_rate"] = str(
                device_variables["interfaces"][inet_ifname]["bandwidth"])  # noqa: E501
            device_variables[f"internet{circuit_index}_if_secondary_address"] = "TEMPLATE_IGNORE"

            inet_main_ifname = inet_ifname.split('.')[0]
            inet_main_if = device_variables["interfaces"][inet_main_ifname]
            if not inet_main_if["auto_negotiate"]:
                log.error("auto_negotiate NOT configured for Internet!!!!!")

            # nexthop for internet service

            if self.get_vpn0_gw(device_variables, inet_ifname):
                device_variables[f"vpn0_next_hop_ip_address{circuit_index}"] = self.get_vpn0_gw(
                    device_variables, inet_ifname)  # noqa: E501
                device_variables[f"default{circuit_index}_prefix"] = "0.0.0.0/0"
            else:
                # dhcp on wan if
                device_variables[f"vpn0_next_hop_ip_address{circuit_index}"] = "TEMPLATE_IGNORE"
                device_variables[f"default{circuit_index}_prefix"] = "TEMPLATE_IGNORE"

            circuit_nr = circuit_nr + 1

            if circuit_index == "":
                circuit_index = 1

            circuit_index = int(circuit_index) + 1

    def update_device_template(self, device_conf: dict, device_template: dict) -> dict:
        """update device template with Office Compute."""
        self.template = self._render_template_file(device_conf)
        return self.merge_generalTemplates(self.template, device_template)
