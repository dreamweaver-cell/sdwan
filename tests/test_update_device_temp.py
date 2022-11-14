"""Test module for capwap, dc_gwms, firewall"""
from ast import Dict
from pyclbr import Function
from tokenize import Double
from typing import List, Tuple

import pytest

from snap.device import Device
from snap.service import Service
from tests.helper import d4k, d4k_firewall, d4k_voice, loadservices


def services(d: Device) -> tuple:
    d = loadservices(d)
    return d.device_variables, d.device_template


@pytest.fixture(autouse=True)
def device_conf_d4k_voice(d4k_voice: list) -> tuple:  # noqa: F811
    return services(d4k_voice)


@pytest.fixture(autouse=True)
def device_conf_d4k(d4k: list) -> tuple:  # noqa: F811
    return services(d4k)


@pytest.fixture(autouse=True)
def device_conf_d4k_firewall(d4k_firewall: list) -> Tuple:  # noqa: F811
    return services(d4k_firewall)


def test_capwap(device_conf_d4k: tuple):
    device_conf, device_template = device_conf_d4k
    service = Service(name="capwap")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_dc_gwms(device_conf_d4k: tuple):
    device_conf, device_template = device_conf_d4k
    service = Service(name="dc_gwms")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_dualrouter(device_conf_d4k_voice: tuple):
    device_conf, device_template = device_conf_d4k_voice
    service = Service(name="dual_router")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_firewall(device_conf_d4k_firewall: tuple):
    device_conf, device_template = device_conf_d4k_firewall
    service = Service(name="firewall")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_internet(device_conf_d4k: tuple):
    device_conf, device_template = device_conf_d4k
    service = Service(name="internet")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_lan(device_conf_d4k: tuple):
    device_conf, device_template = device_conf_d4k
    service = Service(name="lan")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_atea_screen(device_conf_d4k: tuple):
    device_conf, device_template = device_conf_d4k
    service = Service(name="office_atea_screen")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_office_compute(device_conf_d4k_voice: tuple):
    device_conf, device_template = device_conf_d4k_voice
    service = Service(name="office_compute")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_office_ds_switch_ospfv3(device_conf_d4k_voice):
    device_conf, device_template = device_conf_d4k_voice
    service = Service(name="office_ds_switch_ospfv3")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_office_facitity(device_conf_d4k_voice):
    device_conf, device_template = device_conf_d4k_voice
    service = Service(name="office_facility")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_office_flowscape(device_conf_d4k_voice):
    device_conf, device_template = device_conf_d4k_voice
    service = Service(name="office_flowscape")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_office_hm_wifi_data(device_conf_d4k_voice):
    device_conf, device_template = device_conf_d4k_voice
    service = Service(name="office_hm_wifi_data")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_office_ospf(device_conf_d4k_voice):
    device_conf, device_template = device_conf_d4k_voice
    service = Service(name="office_ospf")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_office_printer(device_conf_d4k_voice):
    device_conf, device_template = device_conf_d4k_voice
    service = Service(name="office_printer")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_office_thin_clients(device_conf_d4k):
    device_conf, device_template = device_conf_d4k
    service = Service(name="office_thin_clients")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_office_voice(device_conf_d4k_voice):
    device_conf, device_template = device_conf_d4k_voice
    service = Service(name="office_voice")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_office_wlan_ap(device_conf_d4k_voice):
    device_conf, device_template = device_conf_d4k_voice
    service = Service(name="vlan332_external_partners")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_vlan315_security_camera(device_conf_d4k_voice):
    device_conf, device_template = device_conf_d4k_voice
    service = Service(name="vlan315_security_camera")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_vlan332_external_partners(device_conf_d4k_voice):
    device_conf, device_template = device_conf_d4k_voice
    service = Service(name="vlan332_external_partners")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_vpls(device_conf_d4k_voice):
    device_conf, device_template = device_conf_d4k_voice
    service = Service(name="vpls")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_zscaler(device_conf_d4k_voice):
    device_conf, device_template = device_conf_d4k_voice
    service = Service(name="zscaler")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_zscaler_ipsec(device_conf_d4k_voice):
    device_conf, device_template = device_conf_d4k_voice
    service = Service(name="zscaler_ipsec")
    service.update_device_template(device_conf, device_template)
    assert device_template


def test_zscaler_pop(device_conf_d4k_voice):
    device_conf, device_template = device_conf_d4k_voice
    service = Service(name="zscaler_pop")
    service.update_device_template(device_conf, device_template)
    assert device_template
