"""Define the VPLS-service"""
import ipaddress

from snap.logger import log
from snap.service import Service


class ServiceVpls(Service):
    """Define VPLS service"""

    name = "vpls"
    provision_order = 100

    def service_logic(self, device_variables: dict, device_template: dict):
        """Function called before updateing templates. All service logic goes here."""
        var = device_variables

        # set vpls variables
        vpls_ifname = var["services"]["vpls"]['interfaces'][0]
        vpls_if = var["interfaces"][vpls_ifname]
        var["vpls_if_name"] = vpls_ifname
        var["vpls_if_description"] = vpls_if.get("description", "VPLS interface")
        var["vpls_if_ipv4_address"] = vpls_if["ipv4"]
        var["vpls_if_mac_address"] = vpls_if["mac_address"]
        var["vpls_shaping_rate"] = str(vpls_if["bandwidth"])
        var["vpls_sub_int"] = False
        var["default3_prefix"] = "0.0.0.0/0"
        var["default4_prefix"] = "0.0.0.0/0"

        # VPLS-region china
        if var['system_host_name'][:2] == "cn":
            var["vpn0_next_hop_ip_address3"] = "10.0.128.3"
            var["vpn0_next_hop_ip_address4"] = "10.0.128.4"
        else:
            var["vpn0_next_hop_ip_address3"] = var["vpls_sdwanpop1_ip"]
            var["vpn0_next_hop_ip_address4"] = var["vpls_sdwanpop2_ip"]

        if not ipaddress.ip_address(var["vpn0_next_hop_ip_address3"]) in ipaddress.ip_network(
                var["vpls_if_ipv4_address"], strict=False):
            log.error("VPLS address not correct subnet for nexthop!")
        # Check if VPLS interface is sub interface (MTU fix)
        if len(vpls_ifname.split(".")) >= 2:
            log.debug(f"VPLS subinterface: {vpls_ifname}")
            var["vpls_sub_int"] = True
            var["parent_vpls_if_name"] = vpls_ifname.split(".")[0]
            var["vpls_sub_int_encap"] = vpls_ifname.split(".")[1]
        # Not needed... changeing feature template
        # var["parent_vpls_if_description"] = var["vpls_if_description"]

    def update_device_template(self, device_conf: dict, device_template: dict) -> dict:
        """update device template with VPLS."""
        self.template = self._render_template_file(device_conf)
        return self.merge_generalTemplates(self.template, device_template)

    def validate_service(self):
        """Tests service"""
        pass
