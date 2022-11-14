import re

import snap.config as conf
from snap.service import Service
from tests.helper import vars_from_file

device_variables = vars_from_file("snapconf_1k.json")
device_conf = vars_from_file("vars_4k_dual_router_2.json")
device_template = {'configType': 'template', 'generalTemplates': []}

service = Service(name="lan")


def test_service_logic():
    service.service_logic(device_variables, device_template)
    assert service.lan_interface_head in device_template["generalTemplates"]
    assert service.mgmt_interface_head in device_template["generalTemplates"]

    for max_route_id in range(1, conf.MAX_STATIC_ROUTES + 1):
        route = device_variables[f"vpn10_ipv4_route_{max_route_id}"]
        next_hop_ip = device_variables[f"vpn10_next_hop_ip_{max_route_id}"]
        ip_distance = device_variables[f"vpn10_next_hop_ip_distance_{max_route_id}"]
        assert route == "TEMPLATE_IGNORE" or route == "10.156.222.245/32"
        assert next_hop_ip == "TEMPLATE_IGNORE" or next_hop_ip == "10.156.10.4"
        assert ip_distance == "TEMPLATE_IGNORE" or ip_distance == "1"

    for static_route_prefix in device_variables["routing"]["static"]:
        if static_route_prefix["ipv4"] != "0.0.0.0" and static_route_prefix["vrf"] == "vpn10":
            for static_counter in range(1, conf.MAX_STATIC_ROUTES + 1):
                route = device_variables[f"vpn10_ipv4_route_{static_counter}"]
                next_hop_ip = device_variables[
                    f"vpn10_next_hop_ip_{static_counter}"] == static_route_prefix[
                    "nexthop_ip"]
                ip_distance = device_variables[f"vpn10_next_hop_ip_distance_{static_counter}"]
                assert route == "10.156.222.245/32" or route == "TEMPLATE_IGNORE"
                assert ip_distance == "1" or ip_distance == "TEMPLATE_IGNORE"
                assert device_variables['vpn10_static_tracker_name'] == "vpn10_fw_tracker"
                assert device_variables["vpn10_static_tracker_endpoint_ip"] == static_route_prefix[
                       "nexthop_ip"]

                switch_blade_trunks = []
                switch_blade_accessport = []
                for switch_blade_interfaces in device_variables["interfaces"]:
                    if re.match("^GigabitEthernet0/[1-9]/[0-7]", switch_blade_interfaces):
                        if ("trunk" in device_variables["interfaces"][switch_blade_interfaces]
                           ["accessport"]):
                            switch_blade_trunks.append(switch_blade_interfaces)
                    if ("static" in device_variables["interfaces"][switch_blade_interfaces]
                        ["accessport"] or "dynamic" in device_variables["interfaces"]
                            [switch_blade_interfaces]["accessport"]):
                        switch_blade_accessport.append(switch_blade_interfaces)

                for interface_trunk_id in range(1, len(switch_blade_trunks)):
                    assert device_variables[
                        f"trunk_if_{interface_trunk_id}"] == "GigabitEthernet0/1/0"
                    assert device_variables[
                        f"trunk_if_{interface_trunk_id}_allowed_vlans"] == "2,5,12,100,927,928"
                    assert device_variables[
                        f"trunk_if_{interface_trunk_id}_native_vlan"] == device_variables[
                            "interfaces"][
                            device_variables[f"trunk_if_{interface_trunk_id}"]]["native_vlan"]

                for interface_access_id in range(1, len(switch_blade_accessport) + 1):
                    assert device_variables[f"access_if_{interface_access_id}"] == ""
                    assert device_variables[f"access_if_{interface_access_id}_vlan"] == ""

                if "PW" in device_variables["part_number"]:
                    assert device_variables["wlan_int"] == "Wlan-GigabitEthernet0/1/8"
