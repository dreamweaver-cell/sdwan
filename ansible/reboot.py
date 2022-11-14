import logging as log
import os
import sys

import click
from netmiko import ConnectHandler


@click.command()
@click.option("-device", "-d", default=False, help="specify device to be rebooted")
class Netmiko:
    def __init__(self, device):
        self.hostname = device
        self.device_type = "cisco_xe"
        self.username = os.environ.get("TACACS_USERNAME")
        self.password = os.environ.get("TACACS_PASSWORD")
        self.connect_to_device()

    def connect_to_device(self):
        self.conn = ConnectHandler(
            host=self.hostname,
            device_type=self.device_type,
            username=self.username,
            password=self.password,
            port=22,
            conn_timeout=200,
        )
        self.reboot_device()

    def reboot_device(self):
        self.conn.send_command("reload", expect_string="Proceed with reload")
        self.conn.send_command_timing("\n", delay_factor=2)


if __name__ == "__main__":
    """provisioning start"""
    try:
        sys.exit(Netmiko())
    except Exception:
        log.exception("Unhandled exception in main")
