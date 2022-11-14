from pyclbr import Function

import snap.config as cfg
from snap.device import Device
from snap.json_validate import json_validate
from tests.helper import (
    d4kdual_r1_vpls_inet_r2_inet,
    d4kdual_r1_vpls_inet_r2_vpls_inet,
    d4kdual_r1_vpls_r2_inet,
    d4kdual_router_inet_inet,
    loadservices,
    vars_from_file,
)
from zed.dualrouter import RedundantDevice


def runtests(d: Device, varfile: dict):
    loadservices(d)
    vars = d.device_variables

    # template = d.device_template
    # assert get_occurrence_of_value(template, value="PROD-EDGE-INET-INT-STATIC-EMEA") == 1
    json_validate(d.device_template, cfg.JSON_DEVICE_TEMPLATE)

    correct_vars = vars_from_file(varfile)
    for k, v in correct_vars.items():
        assert vars[k] == v


def compare_dict(d: Device, conclusion: dict):
    for key in d:
        assert (key in conclusion and d[key] == conclusion[key])


def test_dual_router_inet_inet(d4kdual_router_inet_inet: Function):  # noqa
    """Test dual router internet-ineternet setup."""
    d1, d2 = d4kdual_router_inet_inet
    runtests(d1, "vars_4k_dual_router_1.json")
    runtests(d2, "vars_4k_dual_router_2.json")


def test_dual_router_primary_vpls_inet_secondary_vpls_internet(
        d4kdual_r1_vpls_inet_r2_vpls_inet: Function):  # noqa
    """_summary_
    TEST primary router VPLS + INTERNET secondary router VPLS + INTERNET

    Args:
        d4kdual_r1_vpls_inet_r2_vpls_inet (_type_): _description_
    """
    device1_obj, device2_obj = d4kdual_r1_vpls_inet_r2_vpls_inet
    device1_obj, device2_obj = RedundantDevice.tloc_update(device1_obj, device2_obj)

    r1r = {
        'dual_router_internet_ipv4': '58.40.147.122/30',
        'internet_source_bw': 1000000,
        'internet_source_pri': 'GigabitEthernet0/0/2',
        'internet_source_sec': 'GigabitEthernet0/0/3',
        'service_interconnect_tloc_destination': True,
        'service_interconnect_tloc_source': False
    }
    r2r = {
        'dual_router_internet_ipv4': '58.40.147.118/30',
        'internet_source_bw': 1000000,
        'internet_source_pri': 'GigabitEthernet0/0/2',
        'service_interconnect_tloc_destination': False,
        'service_interconnect_tloc_source': True
    }

    compare_dict(r1r, device1_obj.primary_data['services']['dual_router'])
    compare_dict(r2r, device2_obj.primary_data['services']['dual_router'])


def test_dual_router_primary_vpls_secondary_internet(d4kdual_r1_vpls_r2_inet: Function):  # noqa
    """
    TEST primary router VPLS + INTERNET secondary router VPLS + INTERNET

    """

    device1_obj, device2_obj = d4kdual_r1_vpls_r2_inet
    device1_obj, device2_obj = RedundantDevice.tloc_update(device1_obj, device2_obj)

    r1r = {
        'dual_router_internet_ipv4': '58.40.147.118/30',
        'internet_source_bw': 1000000,
        'internet_source_pri': 'GigabitEthernet0/0/3',
        'internet_source_sec': 'GigabitEthernet0/0/3',
        'service_interconnect_tloc_destination': True,
        'service_interconnect_tloc_source': False
    }

    r2r = {
        'dual_router_internet_ipv4': '58.40.147.118/30',
        'internet_source_bw': 1000000,
        'internet_source_pri': 'GigabitEthernet0/0/2',
        'internet_source_sec': 'GigabitEthernet0/0/2',
        'service_interconnect_tloc_destination': False,
        'service_interconnect_tloc_source': True
    }

    compare_dict(r1r, device1_obj.primary_data['services']['dual_router'])
    compare_dict(r2r, device2_obj.primary_data['services']['dual_router'])


def test_dual_router_primary_vpls_ineternet_secondary_internet(
        d4kdual_r1_vpls_inet_r2_inet: Function):  # noqa
    """
    TEST primary router VPLS + INTERNET secondary router VPLS + INTERNET

    """

    device1_obj, device2_obj = d4kdual_r1_vpls_inet_r2_inet
    device1_obj, device2_obj = RedundantDevice.tloc_update(device1_obj, device2_obj)

    r1r = {
        'dual_router_internet_ipv4': '58.40.147.122/30',
        'internet_source_bw': 1000000,
        'internet_source_pri': 'GigabitEthernet0/0/2',
        'internet_source_sec': 'GigabitEthernet0/0/3',
        'service_interconnect_tloc_destination': True,
        'service_interconnect_tloc_source': False
    }

    r2r = {
        'dual_router_internet_ipv4': '58.40.147.118/30',
        'internet_source_bw': 1000000,
        'internet_source_pri': 'GigabitEthernet0/0/2',
        'service_interconnect_tloc_destination': False,
        'service_interconnect_tloc_source': True
    }

    compare_dict(r1r, device1_obj.primary_data['services']['dual_router'])
    compare_dict(r2r, device2_obj.primary_data['services']['dual_router'])
