from typing import Tuple

import pytest

from snap import device
from snap.device import Device
from snap.service import Service
from snap.zscaler import ZS
from tests.helper import d4k_voice, loadservices

name = "zscaler_ipsec"

service = Service(name)


@pytest.fixture(autouse=True)
def device_conf_d4k_voice(d4k_voice: Device) -> tuple:  # noqa: F811
    d = loadservices(d4k_voice)
    return d.device_variables, d.device_template


def test_service_logic(device_conf_d4k_voice: Device):
    device_variables, temp = device_conf_d4k_voice
    hostname = device_variables["device_name"]
    service.service_logic(device_variables, temp)
    myvars = device_variables['services'][name]
    assert myvars == {
           'interfaces': ['Tunnel50', 'Tunnel51'], 'enabled': True}
    assert device_variables["ipsec_tunnel50_destination_ip"] == "165.225.114.30"
    assert device_variables["ipsec_tunnel50_remote_id"] == "165.225.114.30"
    assert device_variables["ipsec_tunnel50_pre_shared_secret"] == ZS.presharedkey()
    assert device_variables["ipsec_tunnel50_username"] == ZS.fqdn(hostname)
    assert device_variables["ipsec_tunnel50_source_interface"] == "GigabitEthernet0/0/2"
    assert device_variables["ipsec_tunnel50_ip_address"] == "192.0.2.101/32"
    assert device_variables["ipsec_tunnel51_destination_ip"] == "165.225.226.48"
    assert device_variables["ipsec_tunnel51_remote_id"] == "165.225.226.48"
    assert device_variables["ipsec_tunnel51_pre_shared_secret"] == "d2uS#DD%Gt8#8WOkOT"
    assert device_variables["ipsec_tunnel51_username"] == ZS.fqdn(hostname)
    assert device_variables["ipsec_tunnel51_source_interface"] == "GigabitEthernet0/0/2"
    assert device_variables["ipsec_tunnel51_ip_address"] == "192.0.2.102/32"
