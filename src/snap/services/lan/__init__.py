# flake8: noqa
"""Define the Header-service"""
import logging
import re
from ipaddress import IPv4Network

import snap.config as conf
from snap import SnapConfigError
from snap.service import Service


class ServiceLan(Service):
    """Define head service"""

    name = "lan"
    provision_order = 50

    lan_interface_head = {
        "templateName": "PROD-EDGE-LAN-VPN10-V2",
        "templateType": "cisco_vpn",
        "subTemplates": [],
    }

    mgmt_interface_head = {
        "templateName": "PROD-MGMT-VPN5",
        "templateType": "cisco_vpn",
        "subTemplates": [{
            "templateName": "PROD-MGMT-LO5",
            "templateType": "cisco_vpn_interface"
        }],
    }

    def service_logic_interface_servicetemplates(self):
        """Run the logic for this service."""

        interface_type = "SVI" if "C1111" in self.device_variables["part_number"] else "SUBINT"
        template_type = ("vpn-interface-svi" if "C1111" in self.device_variables["part_number"]
                         else "cisco_vpn_interface")
        for service_interfaces in self.device_variables["services"]["lan"]["interfaces"]:
            vlan_id = (service_interfaces.split("Vlan")[1]
                       if "C1111" in self.device_variables["part_number"] else
                       service_interfaces.split(".")[1])
            if "vpn10" in self.device_variables["interfaces"][service_interfaces]["vrf"]:
                self.lan_interface_head["subTemplates"].append({
                    "templateName":
                        f"PROD-VLAN{ vlan_id }-{ interface_type }-VRRP-{ self.device_variables['redundant_router_type'].upper() }",  # noqa: E501
                    "templateType":
                        f"{ template_type }",
                })
            if "vpn5" in self.device_variables["interfaces"][service_interfaces]["vrf"]:
                self.mgmt_interface_head["subTemplates"].append({
                    "templateName":
                        f"PROD-VLAN{vlan_id}-{interface_type}-VRRP-{self.device_variables['redundant_router_type'].upper()}",  # noqa: E501
                    "templateType":
                        f"{ template_type }",
                })

    def service_logic(self, device_variables: dict, device_template: dict):
        self.template["generalTemplates"] = device_template["generalTemplates"]
        self.device_variables = device_variables
        self.service_logic_interface_servicetemplates()
        self.template["generalTemplates"].append(self.lan_interface_head)
        self.template["generalTemplates"].append(self.mgmt_interface_head)
        """" Take static routing form device variables and add to optional feeld in vManage """
        for max_route_id in range(conf.MAX_STATIC_ROUTES):
            max_route_id = 1 + max_route_id
            device_variables[f"vpn10_ipv4_route_{max_route_id}"] = "TEMPLATE_IGNORE"
            device_variables[f"vpn10_next_hop_ip_{max_route_id}"] = "TEMPLATE_IGNORE"
            device_variables[f"vpn10_next_hop_ip_distance_{max_route_id}"] = "TEMPLATE_IGNORE"

        static_counter = 1
        for static_route_prefix in device_variables["routing"]["static"]:
            if static_route_prefix["ipv4"] != "0.0.0.0" and static_route_prefix["vrf"] == "vpn10":
                if static_counter <= conf.MAX_STATIC_ROUTES:
                    net = IPv4Network(
                        f"{static_route_prefix['ipv4']}/{static_route_prefix['ipv4_mask']}")
                    device_variables[f"vpn10_ipv4_route_{static_counter}"] = net.with_prefixlen
                    device_variables[f"vpn10_next_hop_ip_{static_counter}"] = static_route_prefix[
                        "nexthop_ip"]
                    device_variables[f"vpn10_next_hop_ip_distance_{static_counter}"] = "1"
                    device_variables['vpn10_static_tracker_name'] = "vpn10_fw_tracker"
                    device_variables["vpn10_static_tracker_endpoint_ip"] = static_route_prefix[
                        "nexthop_ip"]
                    static_counter += 1
                else:
                    raise SnapConfigError(
                        f"Too many static routes for vpn10, {static_route_prefix['ipv4']}")

        # Create switch blade configuration for C1k routers.
        if "C1111" in device_variables["part_number"]:
            switch_blade_trunks = []
            switch_blade_accessport = []
            # Get all trunk interfaces on switchblade
            for switch_blade_interfaces in device_variables["interfaces"]:
                if re.match("^GigabitEthernet0/[1-9]/[0-7]", switch_blade_interfaces):
                    if ("trunk" in device_variables["interfaces"][switch_blade_interfaces]
                        ["accessport"]):
                        switch_blade_trunks.append(switch_blade_interfaces)
                    if ("static" in device_variables["interfaces"][switch_blade_interfaces]
                        ["accessport"] or "dynamic" in device_variables["interfaces"]
                        [switch_blade_interfaces]["accessport"]):
                        switch_blade_accessport.append(switch_blade_interfaces)

            # Get all vlans from interface configuration
            switch_blade_vlans = ""
            for switch_blade_vlan_interfaces in device_variables["interfaces"]:
                if "Vlan" in switch_blade_vlan_interfaces:
                    if len(switch_blade_vlans) == 0:
                        switch_blade_vlans = switch_blade_vlan_interfaces.split("Vlan")[1]
                    else:
                        switch_blade_vlans = (switch_blade_vlans +
                                              f",{switch_blade_vlan_interfaces.split('Vlan')[1]}")

            if len(switch_blade_trunks) > 2:
                logging.error("more than 2 trunks on switchblade")
                exit(1)

            interface_trunk_id = 1
            for switch_blade_interfaces_trunk in switch_blade_trunks:
                device_variables[f"trunk_if_{interface_trunk_id}"] = switch_blade_interfaces_trunk
                device_variables[
                    f"trunk_if_{interface_trunk_id}_allowed_vlans"] = switch_blade_vlans
                device_variables[f"trunk_if_{interface_trunk_id}_native_vlan"] = device_variables[
                    "interfaces"][switch_blade_interfaces_trunk]["native_vlan"]
                interface_trunk_id = interface_trunk_id + 1

            interface_access_id = 1
            for switch_blade_interface_access in switch_blade_accessport:
                device_variables[
                    f"access_if_{interface_access_id}"] = switch_blade_interface_access
                device_variables[f"access_if_{interface_access_id}_vlan"] = device_variables[
                    "interfaces"][switch_blade_interface_access]["vlan"]
                interface_access_id = interface_access_id + 1

        # SET WIFI INTERFACE ON
        if "PW" in device_variables["part_number"]:
            device_variables["wlan_int"] = "Wlan-GigabitEthernet0/1/8"
        else:
            device_variables["wlan_int"] = "TEMPLATE-IGNORE"

    def update_device_template(self, device_conf: dict, device_template: dict) -> dict:
        """update device template with Office Compute."""
        if (device_conf):
            self.template = self._render_template_file(device_conf)
            return self.merge_generalTemplates(self.template, device_template)

    def validate_service(self):
        """Tests service"""
        pass
