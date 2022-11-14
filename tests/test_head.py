from snap.service import Service
from tests.helper import vars_from_file

device_variables = vars_from_file("snapconf_1k.json")

service_head = Service(name="head")


def test_get_siteid():
    site_id = service_head.get_siteid(device_variables)
    assert site_id == "10469999"
    assert device_variables["region"] == "emea"


def test_get_systemip():
    ip = service_head.get_systemip(device_variables)
    assert ip == "10.20.28.16"


def test_get_region_variables():
    regional_vars = service_head.get_region_variables(device_variables)
    assert regional_vars["regional_dhcp_helper"] == "10.61.95.125,10.61.95.126"
    assert regional_vars["vpls_sdwanpop1_ip"] == "10.0.0.3"
    assert regional_vars["vpls_sdwanpop2_ip"] == "10.0.0.4"


def test_update_device_variables():
    update = service_head.update_device_variables(device_variables)
    variables = service_head._render_template_file(device_variables, "variables.j2")
    assert variables == {k: v for k, v in variables.items() if k in update}


def test_service_logic():
    service_head.service_logic(device_variables, device_template="")
    assert device_variables["viptela_type"] == "vedge-C1111-8PW"
    assert device_variables["system_ip"] == "10.20.28.16"
    assert device_variables["crypto_sn"] == device_variables["device_serial_number"]
    assert device_variables["snmp_device_location"] == device_variables["device_name"][0:5]
    assert device_variables["internet_if_ipv4_address"] == device_variables["interfaces"][
           device_variables["services"]["internet"]["interfaces"][0]]["ipv4"]

    for lan_interface in device_variables["services"]["lan"]["interfaces"]:
        assert lan_interface.split(".")[0] == "Vlan927" or lan_interface.split(
            ".")[0] == "Vlan928" or lan_interface.split(".")[0] == "Vlan2" or lan_interface.split(
                ".")[0] == "Vlan5" or lan_interface.split(
                    ".")[0] == "Vlan12" or lan_interface.split(
                        ".")[0] == "Vlan100"
