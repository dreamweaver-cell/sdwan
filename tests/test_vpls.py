from snap.service import Service
from tests.helper import vars_from_file

device_variables_cn = vars_from_file("snapconf_4k_voice.json")
device_variables_cn['system_host_name'] = "cn"
device_variables = vars_from_file("snapconf_4k_voice.json")
device_variables['system_host_name'] = ""
device_variables["vpls_sdwanpop1_ip"] = "10.0.0.3"
device_variables["vpls_sdwanpop2_ip"] = "10.0.0.4"
device_template = {}


service = Service("vpls")


def test_service_logic_cn():
    service.service_logic(device_variables_cn, device_template)
    vpls_ifname = device_variables_cn["services"]["vpls"]['interfaces'][0]
    vpls_if = device_variables_cn["interfaces"][vpls_ifname]
    assert device_variables_cn["vpls_if_name"] == vpls_ifname
    assert device_variables_cn["vpls_if_description"] == vpls_if.get("description",
                                                                     "VPLS interface")
    assert device_variables_cn["vpls_if_ipv4_address"] == vpls_if["ipv4"]
    assert device_variables_cn["vpls_if_mac_address"] == vpls_if["mac_address"]
    assert device_variables_cn["vpls_shaping_rate"] == str(vpls_if["bandwidth"])
    assert device_variables_cn["vpls_sub_int"] == False  # noqa: E712
    assert device_variables_cn["default3_prefix"] == "0.0.0.0/0"
    assert device_variables_cn["default4_prefix"] == "0.0.0.0/0"

    # VPLS-region china
    assert device_variables_cn["vpn0_next_hop_ip_address3"] == "10.0.128.3"
    assert device_variables_cn["vpn0_next_hop_ip_address4"] == "10.0.128.4"

    # Check if VPLS interface is sub interface (MTU fix)
    if len(vpls_ifname.split(".")) >= 2:
        assert device_variables_cn["vpls_sub_int"] == True  # noqa: E712
        assert device_variables_cn["parent_vpls_if_name"] == vpls_ifname.split(".")[0]
        assert device_variables_cn["vpls_sub_int_encap"] == vpls_ifname.split(".")[1]


def test_service_logic():
    service.service_logic(device_variables, device_template)
    assert device_variables["vpn0_next_hop_ip_address3"] == device_variables["vpls_sdwanpop1_ip"]
    assert device_variables["vpn0_next_hop_ip_address4"] == device_variables["vpls_sdwanpop2_ip"]
