import os

from netmiko import ConnectHandler


class textfsmconnect:
    def __init__(self, hostname, command, device_type):
        self.hostname = hostname
        self.command = command
        self.device_type = device_type
        self.username = os.environ.get("TACACS_USERNAME")
        self.password = os.environ.get("TACACS_PASSWORD")
        self.textfsm_output = {}
        self.textfsm_connect()

    def textfsm_connect(self):
        self.conn = ConnectHandler(
            host=self.hostname,
            device_type=self.device_type,
            username=self.username,
            password=self.password,
            port=22,
            conn_timeout=200,
        )
        self.textfsm_execute()

    def textfsm_execute(self):
        self.textfsm_output = self.conn.send_command(self.command, use_textfsm=True)
