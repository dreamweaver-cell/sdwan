import os

import snap.config as conf
from snap.device import Device
from snap.json_validate import json_validate
from tests.helper import loadservices

mypath = os.path.dirname(__file__)


def test_device() -> Device:
    d = Device()
    d.load_snapfile(f"{mypath}/support/atgraao1rtrconf.json")
    loadservices(d)


# uuid
    uuid = d.uuid
    assert uuid == f"{d.device_variables['part_number']}-{ d.device_variables['crypto_sn']}"


# get_variable_filename
    directory = f"{conf.ANSIBLE_INVENTORY}/host_vars/{d.hostname}"
    assert d.get_variable_filename(d.hostname) == f"{directory}/{d.hostname}.yml"


# get_device_uuid
    d.in_vmanage()
    device_uuid = d.get_device_uuid(d.uuid)
    assert device_uuid[0]['ncsDeviceName'] == 'vedge-C1111-8PWE-FGL23189180'
    assert device_uuid[0]['system-ip'] == '10.20.15.180'
    assert device_uuid[0]['site-id'] == '10430401'

# read_config_from_file
    d.read_config_from_file(f"{mypath}/support/atgraao1rtrconf.json")
    assert d.hostname == "atgraao1rtr001"
    assert json_validate(d._device_config, conf.JSON_DEVICE_CONFIG_SCHEMA)
    assert d.device_variables == d._device_config


# validate_devicetemplate
    assert json_validate(d.device_template, conf.JSON_DEVICE_TEMPLATE)


# find_generaltemplate
    templatename = d.device_template["generalTemplates"][2]
    result = d.find_generaltemplate(templatename["templateName"])
    assert result == {'templateName': 'PROD-EDGE-OMP-EMEA', 'templateType': 'cisco_omp'}


# delet_from_generaltemplates
    templatename = d.device_template["generalTemplates"][2]
    assert templatename in d.device_template["generalTemplates"]
    result = d.delete_from_generaltemplates(templatename["templateName"])
    assert templatename not in result["generalTemplates"]


# diff_config vmanage
    diff_vmanage = d.diff_config("vmanage")
    assert 'values_changed' in str(diff_vmanage)
    assert 'new_value' in str(diff_vmanage)
    assert 'old_value' in str(diff_vmanage)


# diff_config file
    diff_file = d.diff_config(f"{mypath}/support/comparefile.json")
    assert 'values_changed' in str(diff_file)
    assert 'new_value' in str(diff_file)
    assert 'old_val' in str(diff_file)
