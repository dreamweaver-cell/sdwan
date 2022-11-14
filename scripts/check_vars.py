import yaml

HOSTFILE = "ansible/inventory/host_vars/ausyddc1rtr001/ausyddc1rtr001.yml"
VARS = """vlan5_sub_if_name
vlan5_sec_ipv4_address
vlan5_dhcp_helper
vlan5_vrrp_ipaddress
lo5_ipv4_address
vpn10_ipv4_route_1
vpn10_ipv4_route_2
vpn10_ipv4_route_3
vpn10_ipv4_route_4
vpn10_ipv4_route_5
vpn10_next_hop_ip_1
vpn10_next_hop_ip_2
vpn10_next_hop_ip_3
vpn10_next_hop_ip_4
vpn10_next_hop_ip_5
vlan77_sub_if_name
vlan77_pri_ipv4_address
vlan77_dhcp_helper
vlan77_vrrp_ipaddress
vlan3921_sub_if_name
vlan3921_sec_ipv4_address
vlan3921_vrrp_ipaddress
vlan928_sub_if_name
vlan927_sub_if_name
vlan12_sub_if_name
vlan12_sec_ipv4_address
vlan12_dhcp_helper
vlan12_vrrp_ipaddress
default_prefix
default2_prefix
default3_prefix
default4_prefix
vpn0_next_hop_ip_address
vpn0_next_hop_ip_address2
vpn0_next_hop_ip_address3
vpn0_next_hop_ip_address4
parent_lan_if_name
ipsec_tunnel51_ip_address
ipsec_tunnel51_source_interface
ipsec_tunnel51_destination_ip
ipsec_tunnel51_pre_shared_secret
ipsec_tunnel51_username
ipsec_tunnel51_remote_id
ipsec_tunnel50_ip_address
ipsec_tunnel50_source_interface
ipsec_tunnel50_destination_ip
ipsec_tunnel50_pre_shared_secret
ipsec_tunnel50_username
ipsec_tunnel50_remote_id
internet_if_name
internet_if_description
internet_if_ipv4_address
internet_shaping_rate
inet_tloc_ext_source_if_name
inet_if_tloc_extension
snmp_device_location
system_host_name
system_latitude
system_longitude
system_system_ip
system_site_id"""

with open(HOSTFILE, "r") as f:
    data = yaml.safe_load(f)

sdwan = data["sdwan"]

for line in VARS.splitlines():
    line = line.strip()
    #    print(f"checking {line}...", end="")

    try:
        var = sdwan[line]
    except KeyError:
        print(f"saknas: {line}")
