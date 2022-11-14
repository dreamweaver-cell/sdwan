""" Pre and Post migration tests """
import sys

import click
from hmnet.netconnect import Netmikoconnect

from snap.config import SNAPSHOT_DIR
from snap.logger import log


class Netverify:
    """PRE AND PROD COLLECTION OF TESTS"""

    def __init__(self):
        self.rwanroutes = self.Rwanroutes()

    def network_pre_snap(self):
        self.rwanroutes.device_hostname = "sesthcc4gpr001"
        self.rwanroutes.filename = "pre_migration.json"
        self.rwanroutes.netmiko = Netmikoconnect(
            self.rwanroutes.device_hostname,
            self.rwanroutes.device_type,
            self.rwanroutes.device_command,
        )
        self.rwanroutes.write_output_to_json_file()

    def network_post_snap(self):
        self.rwanroutes.device_hostname = "sesthcc4gpr001"
        self.rwanroutes.filename = "post_migration.json"
        self.rwanroutes.netmiko = Netmikoconnect(
            self.rwanroutes.device_hostname,
            self.rwanroutes.device_type,
            self.rwanroutes.device_command,
        )
        self.rwanroutes.write_output_to_json_file()

    def network_post_diff(self):
        self.rwanroutes.get_pre_post_routingtable()
        # self.rwanroutes.genie_compare_config()
        self.rwanroutes.compare_list()

    class Rwanroutes:
        """TESTCASE: take a snap-shot of the routing table and save to
        Json file for later comparison
        Methods:
            write_output_to_json_file() : takes the dictionary and dumpes it to Json
            genie_compare_config(): Compare the two snap-shots
            get_pre_post_routingtable(): Open pre and post files"""

        def __init__(self):
            self.device_hostname = None
            self.device_type = "cisco_xe"
            self.device_command = "show ip route vrf HM-DATA"
            self.filename = None
            self.netmiko = None

        def write_output_to_json_file(self):
            for _routing_key, routing_value in self.netmiko.netmiko_output.items():
                routes = routing_value["HM-DATA"]["address_family"]["ipv4"]["routes"].keys()

            with open(f"{SNAPSHOT_DIR}/{self.filename}", "w") as outfile:
                for subnets in routes:
                    outfile.write(f"{subnets}\n")

        def compare_list(self):
            for network_element in self.diff_compare_1:
                if network_element not in self.diff_compare_2:
                    log.warning(f"Network missing: { network_element } ")

        def get_pre_post_routingtable(self):
            self.diff_compare_1 = []
            with open(f"{SNAPSHOT_DIR}/pre_migration.json", "r") as listfile:
                for line in listfile:
                    # remove linebreak which is the last character of the string
                    currentplace = line[:-1]
                    # add route to  list
                    self.diff_compare_1.append(currentplace)

            self.diff_compare_2 = []
            with open(f"{SNAPSHOT_DIR}/post_migration.json") as listfile:
                for line in listfile:
                    # remove linebreak which is the last character of the string
                    currentplace2 = line[:-1]
                    # add route to  list
                    self.diff_compare_2.append(currentplace2)


# this click will not work in click 8 remove default=True
@click.command()
@click.option("--run", default=True, help="pre / post verifiaction.")
def run(run: str):
    """main function for netverify"""
    # TODO: parse command line for post/premigration and hostname
    if run == "pre":
        pre_migration = Netverify()
        pre_migration.network_pre_snap()

    if run == "post":
        post_migration = Netverify()
        post_migration.network_post_snap()

    if run == "diff":
        post_migration = Netverify()
        post_migration.network_post_diff()


if __name__ == "__main__":
    try:
        sys.exit(run())
    except Exception:
        log.exception("Unhandled exception in main")
