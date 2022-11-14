from nested_lookup import get_occurrence_of_value

import snap.config as cfg
from snap import device
from snap.device import Device
from snap.json_validate import json_validate
from tests.helper import d1k, d4k, d4k_dual_inet, d4k_zs, loadservices  # noqa


def test_config():
    assert cfg.snapdir
    assert cfg.DB_KEY
    assert cfg.SNAPCONF_DIR


def test_snapconfig_4kzs(d4k_zs: Device):  # noqa
    var = d4k_zs.device_variables
    assert var["device_name"] == "sesthxx3rtr001"
    assert "head" in d4k_zs.services
    assert "vpls" in d4k_zs.services
    assert "GigabitEthernet0/0/1" in var["services"]["internet"]["interfaces"]
    assert "GigabitEthernet0/0/0" in var["services"]["vpls"]["interfaces"]
    assert var['device_serial_number'] == "FOC12345R9A"
    assert var["system_longitude"] == "13.000000"
    json_validate(d4k_zs._device_config, cfg.JSON_DEVICE_CONFIG_SCHEMA)


def test_services_4kzs(d4k_zs: Device):  # noqa
    d = loadservices(d4k_zs)
    var = d.device_variables
    assert var["system_ip"] == "10.20.12.188"
    assert var["system_site_id"] == "10469999"
    assert var["vpls_if_mac_address"] == "01:23:45:67:89:AB"
    assert var["vpn0_next_hop_ip_address3"] == "10.0.0.3"
    assert var["vpn0_next_hop_ip_address4"] == "10.0.0.4"
    assert var["default_prefix"] == "0.0.0.0/0"
    assert var["default3_prefix"] == "0.0.0.0/0"
    assert var["default4_prefix"] == "0.0.0.0/0"

    json_validate(d.device_template, cfg.JSON_DEVICE_TEMPLATE)

    # check old zscaler config
    zs_inbase = d.find_generaltemplate('PROD-EDGE-VPN0-V2')
    gre = [d for d in zs_inbase['subTemplates'] if d['templateName'] == "PROD-EDGE-GRE50"]
    assert gre[0]["templateName"] == "PROD-EDGE-GRE50"

    # check guest-wifi
    zs_inbase = d.find_generaltemplate('PROD-EDGE-GUEST-VPN900')
    gre = [
        d for d in zs_inbase['subTemplates']
        if d['templateName'] == "PROD-VLAN927-SUBINT-VRRP-PRI"  # noqa E501
    ]


def test_snapconfig_4k(d4k: Device):  # noqa
    """test basic 4k without VPLS, ZS or guestwifi"""
    var = d4k.device_variables
    assert var["device_name"] == "sesthxx3rtr001"
    assert "head" in d4k.services
    assert "GigabitEthernet0/0/1" in var["services"]["internet"]["interfaces"]
    json_validate(d4k._device_config, cfg.JSON_DEVICE_CONFIG_SCHEMA)


def test_services_4k(d4k: Device):  # noqa
    d = loadservices(d4k)
    var = d.device_variables
    assert var["system_ip"] == "10.20.12.188"
    assert var["system_site_id"] == "10469999"
    assert var["default_prefix"] == "0.0.0.0/0"
    json_validate(d.device_template, cfg.JSON_DEVICE_TEMPLATE)

    # check that zscaler-config is not in template
    zs_inbase = d.find_generaltemplate('PROD-EDGE-VPN0-V2')
    gre = [d for d in zs_inbase['subTemplates'] if d['templateName'] == "PROD-EDGE-GRE50"]
    assert gre == []


def test_services_1k(d1k: Device):  # noqa

    # check base variables
    d = loadservices(d1k)
    var = d.device_variables
    assert "Vlan5" in var["interfaces"] and "Vlan5" in var["services"]["lan"]["interfaces"]
    assert var["vlan5_pri_ipv4_address"] == "10.20.16.66/29"
    assert var["viptela_type"] == "vedge-C1111-8PW"
    ''' validate device configuration '''
    # check managment vlan 5
    onek_inbase = d.find_generaltemplate('PROD-MGMT-VPN5')
    vlan5 = [
        d for d in onek_inbase['subTemplates'] if d['templateName'] == "PROD-VLAN5-SVI-VRRP-PRI"
    ]  # noqa E501
    assert vlan5[0]["templateName"] == "PROD-VLAN5-SVI-VRRP-PRI"

    assert d.device_template['deviceType'] == "vedge-C1111-8PW"
    assert d.device_template['templateName'] == "sesthit8rtr001-snap"
    assert d.device_template['policyName'] == "PROD-EDGE-LOCAL-POLICY"

    json_validate(d.device_template, cfg.JSON_DEVICE_TEMPLATE)


def test_dual_internte_4k(d4k_dual_inet: Device):  # noqa
    # check if dual internet i service
    d = loadservices(d4k_dual_inet)
    var = d.device_variables
    template = d.device_template
    assert len(var["services"]["internet"]["interfaces"]) <= 2
    # Single router Primary internet
    assert var['internet_if_name'] == "GigabitEthernet0/0/1"
    assert var['internet_shaping_rate'] == "300000"
    assert var['internet_if_ipv4_address'] == "213.155.147.194/29"
    assert var['vpn0_next_hop_ip_address'] == "213.155.147.193"
    assert var['ipsec_tunnel50_source_interface'] == 'GigabitEthernet0/0/1'
    assert get_occurrence_of_value(template, value="PROD-EDGE-INET-INT-STATIC-NAT-EMEA") == 1

    # Sinble router secondary internet
    assert var['internet2_if_name'] == "GigabitEthernet0/0/2"
    assert var['internet2_shaping_rate'] == "300000"
    assert var['internet2_if_ipv4_address'] == "213.155.147.202/29"
    assert var['vpn0_next_hop_ip_address2'] == "213.155.147.201"
    assert var['ipsec_tunnel51_source_interface'] == "GigabitEthernet0/0/2"
    assert get_occurrence_of_value(template, value="PROD-EDGE-INET-INT2-STATIC-EMEA") == 1
    # Template

    json_validate(d.device_template, cfg.JSON_DEVICE_TEMPLATE)
