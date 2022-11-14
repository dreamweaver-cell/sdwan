# flake8: noqa: C901
# import os
import json
import pprint
import re
import sys

import click
from nested_lookup import nested_lookup

import zed.config as cfg
from snap.device import Device
from snap.logger import log, log_init
from snap.services import vlan315_security_camera, vlan332_external_partners
from zed.dualrouter import RedundantDevice

from .migration import Migration
from .textfsmconnect import textfsmconnect


@click.command()
@click.option("--device", "-d", help="specify device to be migrated")
@click.option("--debug/--no-debug", "-d", help="Enable / disable debug output.")
def main(debug, device: str):
    """initiates provisioning process"""
    log_init(debug)
    log.info("Starting data collection")
    mdevice = Migration()
    mdevice.device = device
    mdevice.host_vars = {}

    if mdevice.verify_ssh_connectivity(mdevice.device, 22, 1):
        log.info(f"*** starting config collection {mdevice.device} ***")
    else:
        log.warning("provisioning end due to connectivity issues")
        exit(0)

    # Fetch Base variables from Cisco Prime
    log.debug("Fetch Crytpo PKI from router")
    mdevice.base_prime_data = mdevice.get_host_from_cisco_prime(mdevice.device)

    # Fetch Crytpo PKI from router
    # mdevice.crypto_pki = mdevice.genie_crypto_pki(mdevice.device)
    # certificate_section = nested_lookup("certificate", mdevice.crypto_pki.netmiko_output)
    log.debug("Fetch SUID")
    certificate_section = textfsmconnect(device, "show crypto pki certificates CISCO_IDEVID_SUDI",
                                         "cisco_xe")

    # Fetch static-route from router
    log.debug("Fetch static-route")
    show_ip_route_static = textfsmconnect(device, "show run | i ip route", "cisco_xe")
    # if type(show_ip_route_static.textfsm_output) != list:
    #    show_ip_route_static.textfsm_output = [f"{show_ip_route_static.textfsm_output}"]

    # Fetch access-ports and trunkports on C1111-PW switch
    #
    # show_interfaces_switchport = textfsmconnect(device,
    #                                            "show interfaces switchport",
    # "cisco_xe")

    # Fetch If voice is configured
    log.debug("check voice")
    show_run_vrf_voice_vrf = textfsmconnect(device, "show run | inc voice vrf", "cisco_xe")

    if len(show_run_vrf_voice_vrf.textfsm_output) > 0:
        log.error(f"VOICE VRF CONFIGURED on {device} EXIT(1)")
        office_voice = True
        # exit(1)
    else:
        office_voice = False


    # Check if primary router
    redundant_router_type = mdevice.router_type(device)
    # response = os.system("ping -c 1 -t 1 -W 1 " + "127.0.0.100 2>&1 >/dev/null")

    # Fetch interfaces from router
    show_interface = mdevice.genie_show_interfaces(device)
    mdevice.host_vars["interface"] = {}
    show_interface_extract = [
        "description",
        "bandwidth",
        "auto_negotiate",
    ]

    interface = mdevice.genie_extract_interfaces(show_interface, mdevice.host_vars["interface"],
                                                 show_interface_extract)

    # Fetch ip interfaces from router
    mdevice.host_vars["ip_interface"] = {}
    show_ip_interface = mdevice.genie_show_ip_interfaces(device)
    print(show_ip_interface)
    show_ip_interface_extract = [
        "helper_address",
        "vrf",
        "mtu",
        "ipv4",
    ]

    ip_interface = mdevice.genie_extract_interfaces(show_ip_interface,
                                                    mdevice.host_vars["ip_interface"],
                                                    show_ip_interface_extract)

    # combine interface and ip_interface dictionary
    mdevice.combine_interfaces(ip_interface, interface)

    # Extract services from configuration
    mdevice.extract_services()
    # pprint.pprint(mdevice.extract_services())
    # Extract tunnel destination if zscaler is configured
    # print("Fetch zscaler tunnel ")
    if "zscaler" in mdevice.services:
        show_run_int_tun_50 = textfsmconnect(device, "show running-config interface tunnel50",
                                             "cisco_xe")
        show_run_int_tun_51 = textfsmconnect(device, "show running-config interface tunnel51",
                                             "cisco_xe")

    # Update mdevice.host_vars
    try:
        mdevice.host_vars["version"] = cfg.ZEDVERSION
        mdevice.host_vars["device_name"] = mdevice.device
        mdevice.host_vars["part_number"] = nested_lookup("partNumber", mdevice.base_prime_data)[0]
        mdevice.host_vars["software_version"] = nested_lookup("softwareVersion",
                                                              mdevice.base_prime_data)[0]
    except IndexError:
        log.info("Collecting data from prime failed, please contact system administrator")

    mdevice.host_vars["device_serial_number"] = certificate_section.textfsm_output[0]["serial_nr"]
    # serial number in hex anvands bara nar devicen laggs till i PnP-portalen. Behovs inte av provisioneringen.
    # Filtret plockar ut CA-certets serie nr. Ska fixas innan vi kan använda det.
    # mdevice.host_vars["serial_number_in_hex"] = certificate_section.textfsm_output[0]["hex_serial"]
    mdevice.host_vars["routing"] = {"static": show_ip_route_static.textfsm_output or []}
    mdevice.host_vars["redundant_router_type"] = redundant_router_type
    mdevice.host_vars["services"] = mdevice.services
    mdevice.host_vars["interfaces"] = mdevice.interface

    # TODO: REMOVE FROM THIS SECTION SHOULD BE IN SNAP
    # for route in mdevice.host_vars["routing"]["static"]:
    #    if route["vrf"] == "INTERNET-A":
    #        mdevice.host_vars["vpn0_next_hop_ip_address"] = route["nexthop_ip"]
    """
    FIX COLLECTION

    - Add zscaler variables if found
    - Update C1111 with accessport configuration and vlan data
    - Change Vlan100 from vpn12 to vpn10
    - Cleanup data

    """
    # Update Zscaler specific information
    '''
    if "zscaler" in mdevice.services:
        mdevice.host_vars["interfaces"]["Tunnel50"][
            "destination"] = show_run_int_tun_50.textfsm_output[0]["dest"]
        mdevice.host_vars["interfaces"]["Tunnel50"]["source"] = show_run_int_tun_50.textfsm_output[
            0]["source"]
        mdevice.host_vars["interfaces"]["Tunnel51"][
            "destination"] = show_run_int_tun_51.textfsm_output[0]["dest"]
        mdevice.host_vars["interfaces"]["Tunnel51"]["source"] = show_run_int_tun_51.textfsm_output[
            0]["source"]
    '''
    # Check for configured mac-address on VPLS connections
    if "vpls" in mdevice.services:
        # pprint.pprint(f"this is the interface {mdevice.services['vpls']}")
        vpls_physical_interface = mdevice.services['vpls']['interfaces'][0].split(".")[0]
        show_run_int_mac_address = textfsmconnect(device,
                                                  f"show run interface {vpls_physical_interface}",
                                                  "cisco_xe")
        if len(show_run_int_mac_address.textfsm_output):
            mdevice.host_vars["interfaces"][mdevice.services['vpls']['interfaces'][0]]["mac_address"] = \
                mdevice.format_mac(show_run_int_mac_address.textfsm_output[0]["mac_address"])
            log.info(mdevice.host_vars["interfaces"][mdevice.services['vpls']['interfaces'][0]]["mac_address"])
        else:
            # print(mdevice.host_vars["interfaces"][mdevice.services['vpls']['interface'][0]]["phys_address"])
            mdevice.host_vars["interfaces"][mdevice.services['vpls']['interfaces'][0]]["mac_address"] = \
                mdevice.format_mac(mdevice.host_vars["interfaces"]
                                   [mdevice.services['vpls']['interfaces'][0]]
                                   ["phys_address"])

    # FIX: Get extra variables from Cisco 1K devices, switchport access <vlan>
    if "C1111" in nested_lookup("partNumber", mdevice.base_prime_data)[0]:
        show_interfaces_switchport = textfsmconnect(device, "show interfaces switchport",
                                                    "cisco_xe")
        mdevice.add_c1k_specifics(show_interfaces_switchport.textfsm_output)

    # FIX: Put Vlan100 Voice vlan to vpn10
    mdevice.vlan100_to_vpn10()

    # Do some clean up
    del mdevice.host_vars["ip_interface"]
    del mdevice.host_vars["interface"]
    log.debug(json.dumps(mdevice.host_vars))
    # Validate and recalculate values
    mdevice.rebuild_ipv4_interface()
    # pprint.pprint(mdevice.host_vars)
    # Translate STH-CLIENT and MGMT to vManage VPN names
    mdevice.translate_vpn_names()

    # Add standby address on service interfaces
    mdevice.setup_standby_address("lan")
    mdevice.setup_standby_address("mgmt")

    if "capwap" in mdevice.services:
        mdevice.setup_standby_address("capwap")
    if "office_facility" in mdevice.services:
        mdevice.setup_standby_address("office_facility")
    if "office_printer" in mdevice.services:
        mdevice.setup_standby_address("office_printer")
    if "office_compute" in mdevice.services:
        mdevice.setup_standby_address("office_compute")
    if "office_hm_wifi_data" in mdevice.services:
        mdevice.setup_standby_address("office_hm_wifi_data")
    if "firewall" in mdevice.services:
        mdevice.setup_standby_address("firewall")
    if "office_atea_screen" in mdevice.services:
        mdevice.setup_standby_address("office_atea_screen")
    if "vlan315_security_camera" in mdevice.services:
        mdevice.setup_standby_address("vlan315_security_camera")
    if "vlan332_external_partners" in mdevice.services:
        mdevice.setup_standby_address("vlan332_external_partners")
    if "office_flowscape" in mdevice.services:
        mdevice.setup_standby_address("office_flowscape")
    if office_voice:
        mdevice.addvoice()

    # Evaluate and fix exceptions
    mdevice.get_exceptions()

    # write the host_var dict to JSON file
    mdevice.dump_host_var_to_yaml()
    if mdevice.host_vars["redundant_router_type"] == "sec":
        device1_obj = RedundantDevice(mdevice.host_vars["device_name"].split('002')[0] + '001')
        device2_obj = RedundantDevice(mdevice.host_vars["device_name"])
        device1_obj, device2_obj = RedundantDevice.tloc_update(device1_obj, device2_obj)
        # device2_obj = RedundantDevice.rename_zscaler_to_ipsec(device2_obj) # Removed du to migration to zscaler
        device1_obj, device2_obj = RedundantDevice.add_zscaler_interfaces_if_not_found(
            device1_obj, device2_obj)
        # print(device1_obj.primary_data)
        # pprint.pprint(vars(device2_obj))
        RedundantDevice.dump_host_var_to_json(device1_obj.primary_data)
        RedundantDevice.dump_host_var_to_json(device2_obj.primary_data)
        device1_obj.primary_data = None
        device2_obj.primary_data = None
        pprint.pprint(vars(device1_obj))
        pprint.pprint(vars(device2_obj))
        # Print some random stuff
        # pprint.pprint(mdevice.host_vars)
        # pprint.pprint(show_ip_interface.netmiko_output)


if __name__ == "__main__":
    """start inventation"""
    try:
        sys.exit(main())
    except Exception:
        log.exception("Unhandled exception in main")
