from snap.service import Service
from tests.helper import vars_from_file

device_variables = vars_from_file("snapconf_1k.json")
device_template: dict = {}
internet_interface = "GigabitEthernet0/0/0"

service = Service(name="internet")


def test_get_vpn0_gw():
    ip = service.get_vpn0_gw(device_variables, internet_interface)
    assert ip == "185.212.21.49"


def test_service_logi():
    service.service_logic(device_variables, device_template)

    circuit_index = ""

    inet_ifname = "GigabitEthernet0/0/0"
    dhcp = device_variables["dhcp_for_vpn0"]
    if dhcp is not None:
        assert dhcp == "dhcp"
    assert device_variables[f"internet{circuit_index}_if_name"] == str(inet_ifname)
    assert device_variables[f"internet{circuit_index}_if_ipv4_address"] == device_variables[
        "interfaces"][inet_ifname]["ipv4"]
    assert device_variables[f"internet{circuit_index}_if_description"] == device_variables[
        "interfaces"][inet_ifname]["description"]
    assert device_variables[f"internet{circuit_index}_shaping_rate"] == str(
        device_variables["interfaces"][inet_ifname]["bandwidth"])
    assert device_variables[f"internet{circuit_index}_if_secondary_address"] == "TEMPLATE_IGNORE"

    assert device_variables[f"default{circuit_index}_prefix"] == "0.0.0.0/0"
    assert device_variables[f"vpn0_next_hop_ip_address{circuit_index}"] == "185.212.21.49"
    assert device_variables[f"default{circuit_index}_prefix"] == "0.0.0.0/0"
