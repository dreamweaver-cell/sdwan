"""Help functions for testing."""
import json
import os
from typing import Tuple

import pytest

from snap.device import Device
from snap.service import Service
from zed.dualrouter import DualRouter

mypath = os.path.dirname(__file__)


def d_from_config(filename: str) -> Device:
    d = Device()
    d.read_config_from_file(snapconfig_file=filename)
    return d


def vars_from_file(filename: str) -> dict:
    with open(f"{mypath}/support/{filename}", 'r') as fp:
        vars = json.load(fp)
    return vars


def loadservices(d: Device) -> Device:
    for srv in d.services:
        try:
            S = Service(srv)
            S.service_logic(d.device_variables, d.device_template)
            S.update_device_variables(d.device_variables)
            S.update_device_template(d.device_variables, d.device_template)
        except ValueError:
            print(f"no service {srv}")
    return d


@pytest.fixture
def d4k():
    return d_from_config(f"{mypath}/support/snapconf_4k.json")


@pytest.fixture
def d4k_zs():
    return d_from_config(f"{mypath}/support/snapconf_4k_zs.json")


@pytest.fixture
def d4k_zsipsec():
    return d_from_config(f"{mypath}/support/snapconf_4k_zsipsec.json")


@pytest.fixture
def d1k():
    return d_from_config(f"{mypath}/support/snapconf_1k.json")


@pytest.fixture
def d4k_voice():
    return d_from_config(f"{mypath}/support/snapconf_4k_voice.json")


@pytest.fixture
def d4k_dual_inet():
    return d_from_config(f"{mypath}/support/snapconf_4k_zs_dual_inet.json")


# START dual-router tests <tempmidus>#


@pytest.fixture
def d4kdual_router_inet_inet():
    return d_from_config(f"{mypath}/support/snapconf_4k_dual_router_1.json"), d_from_config(
        f"{mypath}/support/snapconf_4k_dual_router_2.json")  # noqa


@pytest.fixture
def d4kdual_r1_vpls_inet_r2_vpls_inet():
    return DualRouter("snapconfig_dual_router_1_vpls+ineternet", mypath + "/support"), \
        DualRouter("snapconfig_dual_router_2_vpls+ineternet", mypath + "/support")


@pytest.fixture
def d4kdual_r1_vpls_r2_inet():
    return DualRouter("snapconfig_dual_router_1_vpls", mypath + "/support"), \
        DualRouter("snapconfig_dual_router_2_ineternet", mypath + "/support")


@pytest.fixture
def d4kdual_r1_vpls_inet_r2_inet():
    return DualRouter("snapconfig_dual_router_1_vpls+ineternet", mypath + "/support"), \
        DualRouter("snapconfig_dual_router_2_ineternet", mypath + "/support")


# END dual-router tests <tempmidus> #


@pytest.fixture
def d4k_firewall():
    return d_from_config(f"{mypath}/support/snapconf_4k_firewall.json")


@pytest.fixture
def diff_snapconfig_vmanage_output() -> tuple:
    changed_device_templates = ['ADD1, ADD2, ADD3']
    removed_dcevice_templates = ['REM1', 'REM2', 'REM3']
    added_device_templates = ['CHA1, CHA2, CHA3']
    return changed_device_templates, removed_dcevice_templates, added_device_templates
