# flake8: noqa
import json
import pprint

import snap.config as snap_config
from snap.logger import log


class DualRouter:
    """ Reads Json configuration file and extracts services and interfaces """

    def __init__(self, router: str, cfg_path: str = snap_config.SNAPCONF_DIR):
        # Create Ro
        self.hostname = router
        self.cfg_path = cfg_path
        self.device_conf = self.read_device_config()
        self.persona = self.primary_data['redundant_router_type']
        self.service_internet = False
        self.service_internet_int = False
        self.service_vpls = False
        self.service_interconnect = False
        self.service_interconnect_int = False
        self.service_interconnect_tloc_destination = False
        self.service_interconnect_tloc_source = False
        self.services_obj_update()

    def read_device_config(self):
        with open(f'{self.cfg_path}/{self.hostname}.json') as json_file:
            self.primary_data = json.load(json_file)

    def services_obj_update(self):
        """ Fill out primary/secondary router """
        if "internet" in self.primary_data['services']:
            self.service_internet = True
            self.service_internet_int =\
                self.remove_tags(self.primary_data['services']['internet']['interfaces'][0])
        if "vpls" in self.primary_data['services']:
            self.service_vpls = True
            self.service_vpls_int =\
                self.remove_tags(self.primary_data['services']['vpls']["interfaces"][0])
        if "interconnect" in self.primary_data['services']:
            self.service_interconnect = True
            self.service_interconnect_int =\
                self.remove_tags(self.primary_data['services']['interconnect']["interfaces"][0])

    @staticmethod
    def remove_tags(interface: str) -> str:
        """ removes .123 from interface """
        if "." in interface:
            return interface.split('.')[0]
        else:
            return interface


class RedundantDevice(DualRouter):

    def __init__(self, router: str):
        DualRouter.__init__(self, router)

    def dual_primary_router(device1_obj, device2_obj):
        pass
        # return device1_obj, device2_obj

    def update_router_dict():
        # print(f"hello {RedundantDevice.device1_obj.internet_source_pri}")
        pass

    def rename_zscaler_to_ipsec(device):
        if ("zscaler" in device.primary_data['services']):
            device.primary_data['services']["zscaler_ipsec"] = device.primary_data['services'][
                "zscaler"]
            del device.primary_data['services']["zscaler"]
        return device

    def add_zscaler_interfaces_if_not_found(device_zscaler_int, device_zscaler_int2) -> tuple:
        # add zscaler interfaces
        lan_interface = device_zscaler_int.primary_data['services']['lan']["interfaces"][0].split(
            ".")[0]

        # VPLS + VPLS Does not have any Guest WIFI and only need zscaler_pop service.
        if "vpls" in device_zscaler_int.primary_data['services'] and \
            "vpls" in device_zscaler_int2.primary_data['services'] and \
            "internet" not in device_zscaler_int.primary_data['services'] and \
            "internet" not in device_zscaler_int2.primary_data['services']:
            device_zscaler_int.primary_data['services']['zscaler_pop'] = True
            device_zscaler_int2.primary_data['services']['zscaler_pop'] = True

        else:
            if ("zscaler" not in device_zscaler_int.primary_data['services'] and \
                f"{lan_interface}.927" not in \
                    device_zscaler_int.primary_data['services']['lan']['interfaces']):
                device_zscaler_int.primary_data['services']['lan']['interfaces'].append(
                    f'{lan_interface}.927')
                device_zscaler_int.primary_data['services']['lan']['interfaces'].append(
                    f'{lan_interface}.928')
                device_zscaler_int.primary_data['services']['zscaler_ipsec'] = {}
                device_zscaler_int.primary_data['services']['zscaler_ipsec']['interfaces'] = [
                    "Tunnel50", "Tunnel51"
                ]
                device_zscaler_int.primary_data['interfaces'][f'{lan_interface}.927'] = {
                    "description": "**LIB_HM_WIFI_GUEST**",
                    "bandwidth": 1000000,
                    "port_channel": {
                        "port_channel_member": "false"
                    },
                    "vrf": "vpn900",
                    "inbound_access_list": "ANTISPOOF-LIB-ACL-IN-IPV4",
                    "mtu": 1500,
                    "ipv4": "172.16.0.2/22",
                    "standby": "172.16.0.1"
                }
                device_zscaler_int.primary_data['interfaces'][f'{lan_interface}.928'] = {
                    "description": "**LIB_HM_WIFI_ACCESS**",
                    "bandwidth": 1000000,
                    "port_channel": {
                        "port_channel_member": "false"
                    },
                    "vrf": "vpn900",
                    "inbound_access_list": "ANTISPOOF-LIB-ACL-IN-IPV4",
                    "mtu": 1500,
                    "ipv4": "172.16.8.2/21",
                    "standby": "172.16.8.1"
                }
        return (device_zscaler_int, device_zscaler_int2)

    def tloc_update(device1_obj, device2_obj):
        if (device1_obj.service_internet):
            if (device2_obj.service_vpls):
                if (device2_obj.service_internet and device2_obj.service_vpls):
                    device1_obj.service_interconnect_tloc_destination = True
                else:
                    # Sedondary router does not have Internet or VPLS
                    device1_obj.service_interconnect_tloc_source = True
            else:
                # Secondary router has internet
                if (device2_obj.service_internet):
                    device1_obj.service_interconnect_tloc_destination = True
                else:
                    # Secondary router does not have Internet
                    device1_obj.service_interconnect_tloc_source = True
        else:
            # Primary does not have Internet
            if (device2_obj.service_internet):
                device1_obj.service_interconnect_tloc_destination = True
            else:
                # Secondary router does not have Internet
                log.info("Site router VPLS + VPLS")
                pass

        if (device2_obj.service_internet):
            if (device2_obj.service_vpls):
                if (device1_obj.service_internet and device1_obj.service_vpls):
                    device2_obj.service_interconnect_tloc_source = True
                else:
                    # Primary router does not have Internet or VPLS
                    device2_obj.service_interconnect_tloc_source = True
            else:
                # Secondary router does not have VPLS
                if (device1_obj.service_internet):
                    device2_obj.service_interconnect_tloc_source = True
                else:
                    # Primary router does not have internet
                    device2_obj.service_interconnect_tloc_source = True

        # Secondary has no Internet
        else:
            if (device2_obj.service_vpls):
                if (device1_obj.service_internet):
                    device2_obj.service_interconnect_tloc_destination = True
                else:
                    # Primary does not have Internet
                    log.info("Site router VPLS + VPLS")
                    pass
            else:
                # Secondary does not have VPLS
                log.info("Error unsupported tloc combination")
                exit(1)

        # Updating Object with TLOC extensions
        device1_obj.primary_data['services']['dual_router'] = {}
        device2_obj.primary_data['services']['dual_router'] = {}

        device1_obj.primary_data['services']['dual_router'][
            'service_interconnect_tloc_destination'] = device1_obj.service_interconnect_tloc_destination  # noqa: E501
        device1_obj.primary_data['services']['dual_router']['service_interconnect_tloc_source'] =\
            device1_obj.service_interconnect_tloc_source

        device2_obj.primary_data['services']['dual_router'][
            'service_interconnect_tloc_destination'] = device2_obj.service_interconnect_tloc_destination  # noqa: E501
        device2_obj.primary_data['services']['dual_router']['service_interconnect_tloc_source'] = \
            device2_obj.service_interconnect_tloc_source

        if (device1_obj.service_internet):
            device1_ipv4 = device1_obj.primary_data['interfaces'][device1_obj.primary_data[
                'services']['internet']['interfaces'][0]]['ipv4']  # noqa: E501
            device1_bw = device1_obj.primary_data['interfaces'][device1_obj.primary_data[
                'services']['internet']['interfaces'][0]]['bandwidth']  # noqa: E501
            device1_internet_int = device1_obj.primary_data['services']['internet']['interfaces'][
                0]

        if (device2_obj.service_internet):
            device2_ipv4 = device2_obj.primary_data['interfaces'][device2_obj.primary_data[
                'services']['internet']['interfaces'][0]]['ipv4']  # noqa: E501
            device2_bw = device2_obj.primary_data['interfaces'][device2_obj.primary_data[
                'services']['internet']['interfaces'][0]]['bandwidth']  # noqa: E501
            device2_internet_int = device2_obj.primary_data['services']['internet']['interfaces'][
                0]

        # If internet on both sites compare BW to find out what site should be primary internet
        if (device1_obj.service_internet) and (device2_obj.service_internet):
            if device1_bw == device2_bw:
                device1_obj.primary_data['services']['dual_router'][
                    'internet_source_pri'] = device1_internet_int
                device1_obj.primary_data['services']['dual_router'][
                    'internet_source_sec'] = device1_obj.service_interconnect_int
                device1_obj.primary_data['services']['dual_router'][
                    'dual_router_internet_ipv4'] = device1_ipv4
                device1_obj.primary_data['services']['dual_router'][
                    'internet_source_bw'] = device1_bw
                device2_obj.primary_data['services']['dual_router'][
                    'internet_source_pri'] = device2_internet_int
                device2_obj.primary_data['services']['dual_router'][
                    'dual_router_internet_ipv4'] = device2_ipv4
                device2_obj.primary_data['services']['dual_router'][
                    'internet_source_bw'] = device2_bw

            if device1_bw < device2_bw:
                device1_obj.primary_data['services']['dual_router'][
                    'internet_source_pri'] = device1_obj.service_interconnect_int
                device1_obj.primary_data['services']['dual_router'][
                    'internet_source_sec'] = device1_internet_int
                device1_obj.primary_data['services']['dual_router'][
                    'dual_router_internet_ipv4'] = device2_ipv4
                device1_obj.primary_data['services']['dual_router'][
                    'internet_source_bw'] = device2_bw
                device2_obj.primary_data['services']['dual_router'][
                    'internet_source_pri'] = device2_internet_int
                device2_obj.primary_data['services']['dual_router'][
                    'dual_router_internet_ipv4'] = device2_ipv4
                device2_obj.primary_data['services']['dual_router'][
                    'internet_source_bw'] = device2_bw

            if device1_bw > device2_bw:
                device1_obj.primary_data['services']['dual_router'][
                    'internet_source_pri'] = device1_internet_int
                device1_obj.primary_data['services']['dual_router'][
                    'internet_source_sec'] = device1_obj.service_interconnect_int
                device1_obj.primary_data['services']['dual_router'][
                    'dual_router_internet_ipv4'] = device1_ipv4
                device1_obj.primary_data['services']['dual_router'][
                    'internet_source_bw'] = device1_bw
                device2_obj.primary_data['services']['dual_router'][
                    'internet_source_pri'] = device2_internet_int
                device2_obj.primary_data['services']['dual_router'][
                    'dual_router_internet_ipv4'] = device2_ipv4
                device2_obj.primary_data['services']['dual_router'][
                    'internet_source_bw'] = device2_bw

        # Single router internet
        elif (device2_obj.service_internet) and not (device1_obj.service_internet):
            device1_obj.primary_data['services']['dual_router'][
                'internet_source_pri'] = device1_obj.service_interconnect_int
            device1_obj.primary_data['services']['dual_router'][
                'internet_source_sec'] = device1_obj.service_interconnect_int
            device1_obj.primary_data['services']['dual_router'][
                'dual_router_internet_ipv4'] = device2_ipv4
            device1_obj.primary_data['services']['dual_router']['internet_source_bw'] = device2_bw
            device2_obj.primary_data['services']['dual_router'][
                'internet_source_pri'] = device2_internet_int
            device2_obj.primary_data['services']['dual_router'][
                'internet_source_sec'] = device2_internet_int
            device2_obj.primary_data['services']['dual_router'][
                'dual_router_internet_ipv4'] = device2_ipv4
            device2_obj.primary_data['services']['dual_router']['internet_source_bw'] = device2_bw

        elif (device1_obj.service_internet) and not (device2_obj.service_internet):
            device1_obj.primary_data['services']['dual_router'][
                'internet_source_pri'] = device1_internet_int
            device1_obj.primary_data['services']['dual_router'][
                'internet_source_sec'] = device1_internet_int
            device2_obj.primary_data['services']['dual_router']['internet_source_bw'] = device1_bw
            device1_obj.primary_data['services']['dual_router'][
                'dual_router_internet_ipv4'] = device1_ipv4
            device2_obj.primary_data['services']['dual_router'][
                'internet_source_pri'] = device2_obj.service_interconnect_int
            device2_obj.primary_data['services']['dual_router'][
                'internet_source_pri'] = device2_obj.service_interconnect_int
            device2_obj.primary_data['services']['dual_router'][
                'dual_router_internet_ipv4'] = device1_ipv4
            device2_obj.primary_data['services']['dual_router']['internet_source_bw'] = device1_bw
        return device1_obj, device2_obj

    @staticmethod
    def dump_host_var_to_json(data_obj):
        print("CONF", snap_config.SNAPCONF_DIR)
        with open(f"{snap_config.SNAPCONF_DIR}/{data_obj['device_name']}.json", "w") as file:
            json.dump(data_obj, file, indent=4)


def main(primary: str, secondary: str):
    device1_obj = RedundantDevice(primary)
    device2_obj = RedundantDevice(secondary)
    device1_obj, device2_obj = RedundantDevice.tloc_update(device1_obj, device2_obj)
    pprint.pprint(device1_obj.primary_data["services"]["dual_router"])
    pprint.pprint(device2_obj.primary_data["services"]["dual_router"])
    '''
    device1_obj, device2_obj = RedundantDevice.dual_primary_router(device1_obj, device2_obj)
    RedundantDevice.dump_host_var_to_json(device1_obj.primary_data)
    RedundantDevice.dump_host_var_to_json(device2_obj.primary_data)
    device1_obj.primary_data = None
    device2_obj.primary_data = None
    pprint.pprint(vars(device1_obj))
    pprint.pprint(vars(device2_obj))
    pprint.pprint("\n")
    pprint.pprint(vars(RedundantDevice.device1_obj))
    pprint.pprint(vars(RedundantDevice.device2_obj))
    '''


if __name__ == "__main__":
    main('rtr001', 'rtr002')
