from pyclbr import Function

import pytest

from snap.service import Service

device_variables = {"lo5_ipv4_address": "", "system_ip": "10.20.255.236", "part_number": "ISR4"}
device_variables_2 = {"lo5_ipv4_address": "", "system_ip": "10.20.255.236", "part_number": " "}
device_variables_3 = {"lo5_ipv4_address": "", "system_ip": "10.20.255.236", "part_number":
                      "C1111-8P"}
device_template: dict = {"generalTemplates": []}
device_template_2: dict = {"generalTemplates": []}
device_template_3: dict = {"generalTemplates": []}

service = Service(name="base")


@pytest.fixture()
def service_logic_1() -> None:
    return service.service_logic(device_variables, device_template)


@pytest.fixture()
def service_logic_2() -> None:
    return service.service_logic(device_variables_2, device_template_2)


@pytest.fixture()
def service_logic_3() -> None:
    return service.service_logic(device_variables_3, device_template_3)


def test_service_logic_1(service_logic_1: Function):
    assert device_variables["lo5_ipv4_address"] == "10.20.255.236/32"
    assert device_template["generalTemplates"][0]["templateName"] == "ISR4K_VPN_512_Template"
    assert device_template["generalTemplates"][0]["templateType"] == "cisco_vpn"
    assert device_template["generalTemplates"][0]["subTemplates"][0][
        "templateName"] == "PROD-VPN512-ISR4K"
    assert device_template["generalTemplates"][0]["subTemplates"][0][
        "templateType"] == "cisco_vpn_interface"


def test_service_logic_2(service_logic_2: Function):
    assert device_template_2["generalTemplates"][0][
        "templateName"] == "Factory_Default_Cisco_VPN_512_Template"
    assert device_template_2["generalTemplates"][0][
        "templateType"] == "cisco_vpn"


def test_service_logic_3(service_logic_3: Function):
    assert device_template_3["generalTemplates"][0][
        "templateName"] == "Factory_Default_Cisco_VPN_512_Template"
    assert device_template_3["generalTemplates"][1][
        "templateType"] == "switchport"
