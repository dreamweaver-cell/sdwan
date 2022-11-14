""" Validateion Script """
import json
import unittest

from zed.migration import Migration


class Testzed(unittest.TestCase):
    def setUp(self):
        self.mdevice = Migration()
        self.mdevice.host_vars = {}
        self.mdevice.device = "test_device"
        with open("unittest_files/test_file.json") as json_file:
            self.mdevice.host_vars = json.load(json_file)

    def test_vlan100_to_vpn12(self):
        """
        test that vpn12 is renamed to vpn10
        """
        self.mdevice.vlan100_to_vpn10()
        self.assertEqual("vpn10", self.mdevice.host_vars["interfaces"]["Vlan100"]["vrf"])

    def test_translate_vpn_names(self):
        """
        test that translate_vpn_names works
        """
        self.mdevice.translate_vpn_names()
        self.assertEqual(
            "vpn10", self.mdevice.host_vars["interfaces"]["GigabitEthernet0/0/1"]["vrf"]
        )

        self.assertEqual("vpn5", self.mdevice.host_vars["interfaces"]["Loopback5"]["vrf"])

    def test_setup_standby_address(self):
        """
        Configure Standby address on LAN interfaces
        """
        self.mdevice.setup_standby_address("lan")
        self.assertEqual("10.187.17.82/28", self.mdevice.host_vars["interfaces"]["Vlan12"]["ipv4"])
        self.assertEqual("10.187.17.81", self.mdevice.host_vars["interfaces"]["Vlan12"]["standby"])

    def test_rebuild_ipv4_interface(self):
        """
        Remove Secondary IP on interface and set the primary address
        """
        self.mdevice.rebuild_ipv4_interface()

    def test_get_hostgroup(self):
        _host = self.mdevice.get_hostgroup("sesthit1rtr001")
        self.assertEqual("se", _host[1])
        self.assertEqual("sth", _host[2])
        self.assertEqual("it", _host[3])
        self.assertEqual("1", _host[4])
        self.assertEqual("rtr", _host[5])
        self.assertEqual("001", _host[6])

    def test_service_extractor(self):
        """
        Get the service by interface and ipv4 address
        """
        self.assertEqual(
            "lan", self.mdevice.service_extractor("10.20.30.40", "GigabitEthernet0/0/1.5")
        )
        self.assertEqual(
            "interconnect",
            self.mdevice.service_extractor("10.20.30.40", "GigabitEthernet0/0/1.3902"),
        )
        self.assertEqual(
            "vpls", self.mdevice.service_extractor("10.0.10.20", "GigabitEthernet0/0/1")
        )
        self.assertEqual("zscaler", self.mdevice.service_extractor("10.60.10.20", "Tunnel50"))
        self.assertEqual("zscaler", self.mdevice.service_extractor("10.60.10.20", "Tunnel51"))
        self.assertEqual("guestwifi", self.mdevice.service_extractor("10.60.10.20", "Tunnel55"))
        self.assertEqual("guestwifi", self.mdevice.service_extractor("10.60.10.20", "Tunnel56"))
        self.assertEqual(
            "lan", self.mdevice.service_extractor("10.60.10.20", "GigabitEthernet0/0/1.12")
        )
        self.assertEqual(
            "mgmt_eth", self.mdevice.service_extractor("10.60.10.20", "GigabitEthernet0")
        )


if __name__ == "__main__":
    unittest.main()
