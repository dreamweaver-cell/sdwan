from box import Box

import snap.config as cfg
from snap.device import Device
from snap.json_validate import json_validate
from tests.helper import d4k_zsipsec, loadservices  # noqa


def test_snapconfig_4kzsipsec(d4k_zsipsec: Device):  # noqa
    vars = d4k_zsipsec.device_variables
    assert vars["device_name"] == "sesthxx3rtr001"
    assert "zscaler_ipsec" in d4k_zsipsec.services
    assert "GigabitEthernet0/0/1" in vars["services"]["internet"]["interfaces"]
    json_validate(d4k_zsipsec._device_config, cfg.JSON_DEVICE_CONFIG_SCHEMA)


def test_services_4kzsipsec(d4k_zsipsec: Device, mocker):  # noqa
    mocker.patch("snap.services.zscaler_ipsec.get_zsdestinations",
                 return_value=Box({
                     "primaryIp": "1.1.1.1",
                     "secondaryIp": "2.2.2.2"
                 }))

    d = loadservices(d4k_zsipsec)

    vars = d.device_variables  # noqa
    assert vars["vlan927_sub_if_name"] == "GigabitEthernet0/0/3.927"
    assert vars['vlan927_pri_ipv4_address'] == '172.16.0.2/22'
    assert vars['ipsec_tunnel50_source_interface'] == "GigabitEthernet0/0/1"
    assert vars['ipsec_tunnel50_destination_ip'] == "1.1.1.1"
    assert vars['ipsec_tunnel51_destination_ip'] == "2.2.2.2"
    assert vars['ipsec_tunnel50_pre_shared_secret'] == "d2uS#DD%Gt8#8WOkOT"

    json_validate(d.device_template, cfg.JSON_DEVICE_TEMPLATE)

    zs_inbase = d.find_generaltemplate('PROD-EDGE-VPN0-V2')
    ipsec = [d for d in zs_inbase['subTemplates'] if d['templateName'] == "PROD-EDGE-IPSEC50"]
    assert ipsec[0]["templateName"] == "PROD-EDGE-IPSEC50"

    # check cli template
    zs_inbase = d.find_generaltemplate('PROD-EDGE-CLI-CONFIG-ZSCALER-IPSEC')
    assert zs_inbase
