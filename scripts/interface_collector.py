import json
import pprint
import re

import click

from zed.migration import Migration


@click.command()
@click.option("-device", "-d", help="specify device to be migrated")
def main(device: str):
    mdevice = Migration()
    mdevice.device = device
    mdevice.host_vars = {}

    mdevice.host_vars["ip_interface"] = {}
    show_ip_interface = mdevice.genie_show_ip_interfaces(device)
    show_ip_interface_extract = [
        "vrf",
        "ipv4",
    ]

    ip_interface = mdevice.genie_extract_interfaces(
        show_ip_interface, mdevice.host_vars["ip_interface"],
        show_ip_interface_extract)
    # pprint.pprint(ip_interface)
    vlan_info = {}
    vlan_id = []
    for int_data in ip_interface:
        if re.match("Gi.*[0-9]\/[0-9]\/[0-9]\.[0-9]{1,4}", int_data):  # noqa
            vlan_id.append(int(int_data.split(".")[1]))

    vlan_id.sort()
    vlan_info[device] = vlan_id

    pprint.pprint(vlan_info)
    with open("vlan.txt", "a") as file_object:
        # Append 'vlan' at the end of file
        file_object.write("\n")
        file_object.write(str(json.dumps(vlan_info)))


if __name__ == "__main__":
    """provisioning start"""
    main()
