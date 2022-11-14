from box import Box

import snap.config as cfg
from snap.device import Device
from snap.json_validate import json_validate
from tests.helper import d4k_voice, loadservices  # noqa


def test_snapconfig_4kzsvoice(d4k_voice: Device):  # noqa
    vars = d4k_voice.device_variables
    assert vars["device_name"] == "dehamso1rtr001"
    assert "office_voice" in d4k_voice.services
    json_validate(d4k_voice._device_config, cfg.JSON_DEVICE_CONFIG_SCHEMA)


def test_services_4kzsvoice(d4k_voice: Device, mocker):  # noqa
    mocker.patch("snap.services.zscaler_ipsec.get_zsdestinations",
                 return_value=Box({
                     "primaryIp": "1.1.1.1",
                     "secondaryIp": "2.2.2.2"
                 }))

    d = loadservices(d4k_voice)

    vars = d.device_variables  # noqa
    json_validate(d.device_template, cfg.JSON_DEVICE_TEMPLATE)

    inbase = d.find_generaltemplate('PROD-EDGE-CLI-VOICE-DEHAMSO1RTR001')
    assert inbase

    inbase = d.find_generaltemplate('PROD-EDGE-CLI-CONFIG-ZSCALER-IPSEC')
    assert not inbase
