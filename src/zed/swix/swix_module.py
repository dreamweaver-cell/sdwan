import json
import re

import jsonschema
from definitions import device_dict_phys_interfaes as phy_int, device_obj_interfaces
from services import device_obj_services as switch_service

# from definitions import device_obj
import zed.swix.config as conf
from snap.logger import log, log_init


class device_object(object):
    '''Converts cisco switch iOS configuration to Json structured data. The data
    support textFXM output provided as a list().
    - show version
    - show cdp neighbor
    - show interface switchport
    - show run int vlan5 '''

    def __init__(self, device_dict, obj_hostname):
        #
        # Switch inventory Blueprint
        #
        log_init(False)

        self.obj_hostname = obj_hostname
        self.device_dict = device_dict
        self.device_obj_services = switch_service
        self.device_obj_interfaces = device_obj_interfaces
        self.run()

    @property
    def device_obj_interfaces(self):
        return self._device_obj_interfaces

    @device_obj_interfaces.setter
    def device_obj_interfaces(self, interface_value):
        if isinstance(interface_value, dict):
            self._device_obj_interfaces = interface_value
        else:
            log.info("Interfaces is not a valid dictionary")
            exit(1)

    @property
    def device_obj_services(self):
        return self._device_obj_services

    @device_obj_services.setter
    def device_obj_services(self, service_value):
        if isinstance(service_value, dict):
            self._device_obj_services = service_value
        else:
            log.info("Services is not a valid list")
            exit(1)

    @property
    def device_obj_uplink(self):
        return self._device_obj_uplink

    @device_obj_uplink.setter
    def device_obj_uplink(self, value):
        if isinstance(value, dict):
            self._device_obj_uplink = value
        else:
            log.info("Uplinks not a valid dictionary")
            exit(1)

    @property
    def combined_dict(self):
        return self._combined_dict

    @combined_dict.setter
    def combined_dict(self, combined_value):
        ''' After the dictionaries have been created and combined to one big dicionary,
        we will validate that the data is correct befor we set the combined_dict varible.
        we will first check that JSON file is valid and we will validate it towrds the
        jsonschema template '''
        if json.dumps(combined_value):
            self._combined_dict = combined_value
            log.info("Data valid is a valid Json format")
        else:
            log.info("Data input not an valid Json object")
            exit(1)
        try:
            jsonschema.validate(combined_value, json.load(open(conf.SWIX_JSON_VALIDATE)))
            log.info("Json schema validation successfull")
        except jsonschema.ValidationError as ex:
            if len(ex.path) > 0:
                if self.is_body:
                    detail = ("Invalid input for field '%(path)s'."
                              "Value: '%(value)s'. %(message)s")
                else:
                    detail = ("Invalid input for query parameters "
                              "'%(path)s'. Value: '%(value)s'. %(message)s")
                detail = detail % {
                    'path': ex.path.pop(), 'value': ex.instance,
                    'message': str(ex)
                }
            else:
                detail = ex.message
            log.info(f"Json Validation failure: {detail}")
            exit(1)
        except json.decoder.JSONDecodeError as et:
            log.info(et)
            raise Exception(et)

    def run(self):
        #
        # -= Main program =-
        #
        self.device_obj_interfaces['interfaces'] = self.device_build_interface()
        self.phy_int = self.add_specific_interface_cfg()
        self.device_obj_services['services'] = self.device_build_services()  # Start service build
        self.device_obj_uplinks = self.device_build_uplinks()  # Find switch uplink port

        self.combined_dict = {
            "serial": self.device_dict[0][0]['serial'][0],
            "version": self.device_dict[0][0]['version'],
            "hardware": self.device_dict[0][0]['hardware'][0],
            "ip_address": self.device_dict[4][0]['ip_address'],
            "uplinks": self.device_obj_uplinks,
            "interfaces": self.phy_int,
            "services": self.device_obj_services['services'],
        }

    def device_build_interface(self) -> list:
        _interfaces = []
        for _interface_name in self.device_dict[2]:
            _interfaces.append({
                "name": _interface_name["interface"],
                "vlan": _interface_name["access_vlan"],
                "admin_mode": _interface_name["admin_mode"],
                "enabled": False if _interface_name["mode"] == "down" else True
            })

        return _interfaces

    def device_build_services(self) -> list:
        _servie_list = self.device_obj_services['services']
        for inter_val in self.device_obj_interfaces['interfaces']:
            if inter_val['admin_mode'] == "trunk":
                self.add_interfae_to_trunk(inter_val['name'])
            service = self.find_service(inter_val['vlan'])[0]
            if service == "Unknown":
                self.add_unknown_service(inter_val['vlan'])
            [_servie_list[ixd]['interfaces'].append(inter_val['name'])
                for ixd, _x in enumerate(self.device_obj_services['services'])
                if _x['name'] == service]

        return (_servie_list)

    def device_build_uplinks(self) -> dict:
        #
        # Build uplinks from show cdp neighbor
        #
        _uplink_ports = []
        for router in self.device_dict[1]:
            if "rtr" in router["neighbor"]:
                _uplink_ports.append({
                    "interfaces": router["local_interface"],
                    "type": "router",
                    "name": router["neighbor"].split(".")[0]})
            elif "swi" in router['neighbor']:
                _uplink_ports.append({
                    "interfaces": router["local_interface"],
                    "type": "switch",
                    "name": router["neighbor"].split(".")[0]})
                log.warning("Chained Switch")
            elif "hap" in router['neighbor']:
                self.add_wifi_interface_to_wifi_service(router["local_interface"], "hap")

            elif "lap" in router['neighbor']:
                self.add_wifi_interface_to_wifi_service(router["local_interface"], "lap")

        return _uplink_ports

    def add_interfae_to_trunk(self, _trunk_interface_name):
        #
        # Add interfaces to trunk service
        #
        [self.device_obj_services['services'][ixd]['interfaces'].append(_trunk_interface_name)
            for ixd, _x in enumerate(self.device_obj_services['services'])
            if _x['name'] == "trunk"]

    def add_wifi_interface_to_wifi_service(self, _wifi_interface_name, wifi_service):
        #
        # Add interfaces to wifi service
        #
        # wifi_config = {_wifi_interface_name: {"method": wifi_service}}
        [self.device_obj_services['services'][ixd]['interfaces'].append(_wifi_interface_name)
            for ixd, _x in enumerate(self.device_obj_services['services'])
            if _x['name'] == f"wifi-{wifi_service}"]

    def add_uplinks_interface(self, _uplink_interface_name):
        #
        # Add interfaces to uplink service
        #
        [self.device_obj_services['services'][ixd]['interfaces'].append(_uplink_interface_name)
            for ixd, _x in enumerate(self.device_obj_services['services'])
            if _x['name'] == "uplinks"]

    def add_mgmt_ip_to_mgmt_service(self):
        #
        # return vlan5 ip from show run interface vlan5
        #
        _mgmt_address = [_x['ip_address']
                         for _x in self.device_dict[4]
                         if re.match("^10.*", _x['ip_address'])] or None
        return _mgmt_address

    def add_specific_interface_cfg(self):
        #
        # Match interfaces with full 100/1000
        #
        _port_duplex = [{'name': _x['port'], 'duplex': _x['duplex'], 'speed': _x['speed']}
                        for _x in self.device_dict[3]
                        if re.match("^full.*([0-9]{3,4})", _x['type'])]

        #
        # Set interfaces to "down" if notconnect
        #
        for _enum, _clean in enumerate(_port_duplex):
            if _clean['duplex'] == "notconnect":
                _port_duplex[_enum]['duplex'] = "down"
                _port_duplex[_enum]['speed'] = "down"
        return _port_duplex

    def add_unknown_service(self, _add_service):
        #
        # Add Unknown service
        #
        if not [_z['name']
                for _z
                in self.device_obj_services['services']
                if _z['id'] == _add_service]:
            self.device_obj_services['services'].append({
                "name": "Unknown",
                "id": _add_service,
                "enabled": None,
                "interfaces": []})

    def find_service(self, _id):
        #
        # Return servce name based on vlan id
        #
        return [_z['name']
                for _z
                in self.device_obj_services['services']
                if _z['id'] == _id] or ["Unknown"]
