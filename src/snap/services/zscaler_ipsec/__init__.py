"""
Define the Zscaper IPsec-service
If there is DHCP on the WAN-interface endpoints must be manually configuered.

"""
from box import Box
from restfly import APISession

from snap.logger import log
from snap.service import Service
from snap.zscaler import ZS


def get_zsdestinations(inet_ip: str) -> dict:
    """Get nearest VPN-endpoints based on IP."""
    assert inet_ip and inet_ip != "dhcp_negotiated", "No Inet-ip. DHCP not supported."
    log.info("get destination ip for source ip %s", inet_ip)
    ip = inet_ip.split('/')[0]
    api = APISession(url='https://pac.zscloud.net')

    return api.get(f'getVpnEndpoints?srcIp={ip}', box=Box)


class ServiceZscalerIpsec(Service):
    """Define head service"""

    name = "zscaler_ipsec"
    provision_order = 30
    hostname = ""

    def service_logic(self, device_variables: dict, device_template: dict):
        """Function called before updateing templates. All service logic goes here."""
        self.update_device_variables(device_variables)
        myvars = device_variables['services'][self.name]
        vars = device_variables
        self.hostname = vars["device_name"]
        if vars["redundant_router_type"] == 'sec':
            t50_ip = "192.0.2.103/32"
            t51_ip = "192.0.2.104/32"
        else:
            t50_ip = "192.0.2.101/32"
            t51_ip = "192.0.2.102/32"
        if "dual_router" in vars['services'] and vars["redundant_router_type"] == 'pri':
            t50_src = vars['services']['dual_router']['internet_source_pri']
            t51_src = vars['services']['dual_router']['internet_source_sec']
            inet_ip = vars['services']['dual_router'].get('dual_router_internet_ipv4', '')
        else:
            # TODO...support for dualinternet, single router and VPLS-based internet
            # t50_src = int['Tunnel50']['source']
            t50_src = vars['services']['internet']['interfaces'][0]
            # Check if Single router dual internet.
            if len(vars['services']['internet']["interfaces"]) >= 2:
                t51_src = vars['services']['internet']['interfaces'][1]
            else:
                t51_src = vars['services']['internet']['interfaces'][0]
            inet_ip = vars.get('internet_if_ipv4_address', '')

        zsdest = Box(myvars.get('endpoints') or get_zsdestinations(inet_ip))
        vars["tracker_threshold"] = myvars.get("tracker_threshold", vars["tracker_threshold"])
        vars.update({
            "ipsec_tunnel50_destination_ip": zsdest.primaryIp,
            "ipsec_tunnel50_remote_id": zsdest.primaryIp,
            "ipsec_tunnel50_pre_shared_secret": ZS.presharedkey(),
            "ipsec_tunnel50_username": ZS.fqdn(self.hostname),
            "ipsec_tunnel50_source_interface": t50_src,
            "ipsec_tunnel50_ip_address": t50_ip,
            "ipsec_tunnel51_destination_ip": zsdest.secondaryIp,
            "ipsec_tunnel51_remote_id": zsdest.secondaryIp,
            "ipsec_tunnel51_pre_shared_secret": ZS.presharedkey(),
            "ipsec_tunnel51_username": ZS.fqdn(self.hostname),
            "ipsec_tunnel51_source_interface": t51_src,
            "ipsec_tunnel51_ip_address": t51_ip
        })

    def update_device_template(self, device_conf: dict, device_template: dict) -> dict:
        """update device template with Zscaler."""
        self.template = self._render_template_file(device_conf)
        return self.merge_generalTemplates(self.template, device_template)

    def validate_service(self):
        """Tests service"""
        pass
