# flake8: noqa
import ipaddress
import json
import re
import socket
from ipaddress import IPv4Interface
from typing import Optional

from hmnet.netconnect import Netmikoconnect
from nested_lookup import nested_delete

import snap.config as conf
from snap.logger import log
from snap.services import vlan332_external_partners

from .cisco_prime import Fetchdata


class Migration:

    def __init__(self):
        """Parsing cisco output and structuring data"""
        self.system_host_name = None
        self.host_inventory_json_file = None
        self.host_vars = None
        self.base_prime_data = None
        self.crypto_pki = None

    # self.services = None
    # self.interfaces = None

    def verify_ssh_connectivity(self, host_to_test: str, port: str, timeout: Optional[float]):
        """check that ssh connection can be established"""
        a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        location = (host_to_test, port)
        a_socket.settimeout(timeout)
        result_of_check = a_socket.connect_ex(location)
        if result_of_check == 0:
            log.info("TCP connectivity established")
            return True
        else:
            log.warning("Unable to connect to the device")

    def get_host_from_cisco_prime(self, prime_hostname: str) -> dict:
        prime_object = Fetchdata()
        url = ('data/Devices.json?deviceName=contains( "' + prime_hostname +
               '" )&deviceName=contains("rtr")'
               '&deviceType=contains("Integrated%20Services%20Router")'
               "&.full=true")
        prime_object.get_host_url(url)
        return json.loads(prime_object.httpresponse.text)
        self.base_prime_data = json.loads(prime_object.httpresponse.text)

    # Genie connections
    def genie_crypto_pki(self, host: str) -> Netmikoconnect:
        netmiko_output = Netmikoconnect(host, "cisco_xe",
                                        "show crypto pki certificates CISCO_IDEVID_SUDI")
        return netmiko_output

    def genie_show_interfaces(self, host: str) -> Netmikoconnect:
        netmiko_output = Netmikoconnect(host, "cisco_xe", "show interfaces")
        return netmiko_output

    def genie_show_ip_interfaces(self, host: str) -> Netmikoconnect:
        netmiko_output = Netmikoconnect(host, "cisco_xe", "show ip interface")
        return netmiko_output

    def genie_show_interface_tunnel50(self, host: str) -> Netmikoconnect:
        netmiko_output = Netmikoconnect(host, "cisco_xe", "show run interface Tunnel50")
        return netmiko_output

    def genie_show_interface_mac(self, host: str) -> Netmikoconnect:
        netmiko_output = Netmikoconnect(host, "cisco_xe", "show run interface")
        return netmiko_output

    def genie_extract_interfaces(self, genie_data: Netmikoconnect, deviceinterface, show_interface_extract):
        for interface_name, interfacevalues in genie_data.netmiko_output.items():
            if not deviceinterface.get(interface_name):
                deviceinterface[interface_name] = {}

            for variables in show_interface_extract:
                if variables in interfacevalues:
                    if variables == "description":
                        deviceinterface[interface_name][variables] = \
                        re.sub(r"[^a-zA-Z 0-9-]","",
                        genie_data.netmiko_output[interface_name][variables].strip()[0:128])
                    else:
                        deviceinterface[interface_name][variables] = genie_data.netmiko_output[
                            interface_name][variables]
        return deviceinterface

    def combine_interfaces(self, ip_interface, interface):
        for _ip_interface_key, _ip_interface_value in ip_interface.items():
            for (
                    _ip_interface_key_key,
                    _ip_interface_value_value,
            ) in _ip_interface_value.items():
                interface[_ip_interface_key][_ip_interface_key_key] = _ip_interface_value_value
        self.interface = interface

    def extract_services(self):
        self.services = {}
        for interface_name, ipv4_variable in self.interface.items():
            if "ipv4" in self.interface[interface_name]:
                device_service = self.service_extractor(
                    list(ipv4_variable["ipv4"])[0].split("/")[0], interface_name)
                if device_service not in self.services:
                    self.services[device_service] = {"interfaces":[interface_name], "enabled": True}
                # while migrating to dict we start with internet
                else:
                    self.services[device_service]['interfaces'].append(interface_name)


    def router_type(self, hostname: str):
        device_hostname_groups = self.get_hostgroup(hostname)
        if device_hostname_groups[6] == "001":
            return "pri"
        else:
            return "sec"

    def addvoice(self):
        self.host_vars["services"]["office_voice"] = { "enabled": True, "interfaces":"Looback10" }



    @staticmethod
    def format_mac(mac: str) -> str:
        mac = re.sub("[.:-]", "", mac).lower()
        mac = "".join(mac.split())
        assert len(mac) == 12
        assert mac.isalnum()
        mac = ":".join(["%s" % (mac[i:i + 2]) for i in range(0, 12, 2)])
        return mac

    @staticmethod
    def service_extractor(ipv4_address: str, interface_name: str) -> str:
        """extract services from configuration"""
        """Takes the IPv4 address and sortes it according to RWAN standards
        format: 10.20.2.1, GigabitEthernet"""
        # interfacefunction = "null"
        if re.match(".*[a-z][0]$", interface_name):
            interfacefunction = "mgmt_eth"

        # Firewall Link Network
        elif re.match(".*392[0-1]$", interface_name):
            interfacefunction = "firewall"

        elif re.match(".*180$", interface_name):
            interfacefunction = "capwap"

        # Dist switch ospfv3 interface
        # elif re.match(".*60[0-3]$", interface_name):
        #    interfacefunction = "office_ds_switch_ospfv3"

        elif re.match(".*390[1-2]$", interface_name):
            interfacefunction = "office_ds_switch_ospfv3"

        elif re.match(".*390[7-8]$", interface_name):
            interfacefunction = "office_ds_switch_ospfv3"

        # Service Definitions
        elif re.match(".*[3][9][0-9]{2}$", interface_name):
            interfacefunction = "interconnect"

        # add Voice loopback10 to voice_service if found
        elif re.match("[Ll]oopback10$", interface_name):
            interfacefunction = "office_voice"


        elif re.search(
                r"^([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
                r"(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))"
                r"(?<!127)(?<!^10)"
                r"(?<!^0)\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
                r"(?<!192\.168)(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))\."
                r"([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\."
                r"([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
                r"(?<!\.255$)(?<!\b255.255.255.0\b)(?<!\b255.255.255.242\b)$",
                ipv4_address,
        ):
            interfacefunction = "internet"
        elif re.match("10.0", ipv4_address) and re.match("Tunnel", interface_name):
            interfacefunction = "dmvpn"
        elif re.match("10.0", ipv4_address) and re.match(r"Gigabit", interface_name):
            interfacefunction = "vpls"
        elif re.match("Tunnel50|Tunnel51", interface_name):
            interfacefunction = "zscaler_ipsec"
        elif re.match("Tunnel55|Tunnel56", interface_name):
            interfacefunction = "guestwifi"
        elif re.match("10.20", ipv4_address) and re.match(r"Loopback5", interface_name):
            interfacefunction = "mgmt"

        # VLAN 11 Laser Printer
        elif re.match("^.*\\D11$", interface_name):
            interfacefunction = "office_printer"

        # VLAN 77 IT Facility
        elif re.match("^.*\\D77$", interface_name):
            interfacefunction = "office_facility"

        # VLAN 80 IT Office Compute
        elif re.match("^.*\\D80$", interface_name):
            interfacefunction = "office_compute"

        # VLAN 303 ATEA screens
        elif re.match("^.*\\D303$", interface_name):
            interfacefunction = "office_atea_screen"

        elif re.match("^.*\\D302$", interface_name):
            interfacefunction = "office_flowscape"

        # VLAN 315 Security Cameras
        elif re.match("^.*\\D315$", interface_name):
            interfacefunction = "vlan315_security_camera"

        # VLAN 332 Partners old machines2
        elif re.match("^.*\\D332$", interface_name):
            interfacefunction = "vlan332_external_partners"
        # VLAN 77 HM wifi data
        elif re.match("^.*\\D111$", interface_name):
            interfacefunction = "office_hm_wifi_data"
        else:
            interfacefunction = "lan"

        return interfacefunction

    @staticmethod
    def get_hostgroup(hostname: str):
        """Returnes a re.Match object that includes the hostname devided into
        country, region, function, regioncount.

        Parameters
        ----------
        hostname: str
            hostname: It is mandantory to specify a valid hostname

        Returns
        -------
            returns a re.Match object

        """
        hostgroup = re.search("([a-z]{2})([a-z]{3})([a-z]{2})([1-9]{1,2})([a-z]{3})([0-9]{3})",
                              hostname)
        return hostgroup

    @staticmethod
    def rebuild_lan_ipv4_address(ipv4_network: str) -> list:
        """Calculate primary, secondary, vip_address from ipv4_network"""
        # ipaddress.ip_address(ipv4_network)
        if list(ipv4_network):
            ipv4_network = ipv4_network[0]

        ipv4 = IPv4Interface(ipv4_network)
        ipv4_subnet = ipaddress.IPv4Network(str(ipv4.network))
        vip_ipv4, primary_ipv4, secondary_ipv4 = (
            ipv4_subnet[1],
            ipv4_subnet[2],
            ipv4_subnet[3],
        )

        return [str(vip_ipv4), str(primary_ipv4), str(secondary_ipv4)]

    def rebuild_ipv4_interface(self):
        for service_interface in self.host_vars["interfaces"]:

            if "ipv4" in self.host_vars["interfaces"][service_interface]:
                _ipv4_initial = list(self.host_vars["interfaces"][service_interface]["ipv4"])
                if (len(_ipv4_initial) > 1
                        and service_interface not in self.host_vars["services"]["internet"]["interfaces"]):
                    log.warning(f"Secondary ip configured on router {self.device} EXIT!!")
                    exit(1)

                self.host_vars["interfaces"][service_interface]["ipv4"] = _ipv4_initial[0]

    def setup_standby_address(self, service_type):
        for service_interface in self.host_vars["services"][service_type]['interfaces']:
            matchObj = re.search("Loopback|60[0-3]", service_interface)
            if not matchObj:
                _ipv4_initial = self.host_vars["interfaces"][service_interface]["ipv4"]
                _ipv4_initial_mask = _ipv4_initial.split("/")[1]
                _ipv4_new_ip = self.rebuild_lan_ipv4_address([_ipv4_initial])
                if self.host_vars["redundant_router_type"] == "pri":
                    set_router_ip = _ipv4_new_ip[1]
                else:
                    set_router_ip = _ipv4_new_ip[2]

                if int(_ipv4_initial_mask) < 30:
                    self.host_vars["interfaces"][service_interface][
                        "ipv4"] = f"{set_router_ip}/{_ipv4_initial_mask}"
                self.host_vars["interfaces"][service_interface]["standby"] = f"{_ipv4_new_ip[0]}"
                # pprint.pprint(self.host_vars['interfaces'][service_interface])

    def add_c1k_specifics(self, show_interfaces_switchport: list):
        for C1k_data in show_interfaces_switchport:
            # Rename Gi1/0/1 to GigabitEthernet1/0/1
            if "Gi" in C1k_data["interface_name"]:
                _int = C1k_data["interface_name"].split("Gi")
                self.host_vars["interfaces"][f"GigabitEthernet{_int[1]}"]["accessport"] = C1k_data[
                    "interface_port_mode"]
                self.host_vars["interfaces"][f"GigabitEthernet{_int[1]}"]["vlan"] = C1k_data[
                    "interface_vlan"]
                self.host_vars["interfaces"][f"GigabitEthernet{_int[1]}"]["voice_vlan"] = C1k_data[
                    "interface_voice_vlan"]
                self.host_vars["interfaces"][f"GigabitEthernet{_int[1]}"][
                    "native_vlan"] = C1k_data["native_vlan"]

    def vlan100_to_vpn10(self):
        for vlan100_int in self.host_vars["interfaces"]:
            if re.search(r"\.100|Vlan100", vlan100_int):
                self.host_vars["interfaces"][vlan100_int]["vrf"] = "vpn10"

    def translate_vpn_names(self):
        """translating old vpn name structure to vManage"""
        vpn_translation = {
            "STH-CLIENT": "vpn10",
            "SEC-CLIENT": "vpn10",
            "HKG-CLIENT": "vpn10",
            "MIA-CLIENT": "vpn10",
            "SIN-CLIENT": "vpn10",
            "SYD-CLIENT": "vpn10",
            "CHN-CLIENT": "vpn10",
            "MUM-CLIENT": "vpn10",
            "STH-COMPUTE": "vpn20",
            "SEC-COMPUTE": "vpn20",
            "HKG-COMPUTE": "vpn20",
            "MIA-COMPUTE": "vpn20",
            "SIN-COMPUTE": "vpn20",
            "SYD-COMPUTE": "vpn20",
            "CHN-COMPUTE": "vpn20",
            "MUM-COMPUTE": "vpn20",
            "lan": "vpn12",
            "guest": "vpn900",
            "MGMT": "vpn5",
            "INTERNET-A": "vpn0",
            "ATEASCREEN": "vpn30",
            "machines": "vpn10",
            "machines2": "vpn10"
        }

        for vrf_interface_name in self.host_vars["interfaces"]:
            try:
                self.host_vars["interfaces"][vrf_interface_name]["vrf"] = vpn_translation[
                    self.host_vars["interfaces"][vrf_interface_name]["vrf"]]
            except KeyError:
                pass

        for route in self.host_vars["routing"]["static"]:
            try:
                # print(f"{self.host_vars['routing']['static'][value_dict]['vrf']}")
                route["vrf"] = vpn_translation[route["vrf"]]
            except (KeyError, TypeError):
                pass
    def hotfixclean(self):
        for int in self.host_vars['interfaces']:
            if "Serial" in int \
                or "Service-Engine" in int \
                or "BRI" in int \
                or "Tunnel50" in int \
                or "Tunnel51" in int:
                self.host_vars = nested_delete(self.host_vars, int)

    def dump_host_var_to_yaml(self):
        Migration.hotfixclean(self)
        print("CONF", conf.SNAPCONF_DIR)
        with open(f"{conf.SNAPCONF_DIR}/{self.device}.json", "w") as file:
            json.dump(self.host_vars, file, indent=4)

    def get_exceptions(self):
        """Evaluate and fix regional- and other exceptions."""
        # Check if site is located in china and add zscaler VRF
        if re.match("^cn", self.host_vars["device_name"]):
            self.host_vars["services"]['zscaler_pop'] = True
            self.host_vars["dns_primary"] = "223.5.5.5"
            self.host_vars["dns_secondary"] = "223.6.6.6"
            self.host_vars["tracker_threshold"] = "400"
