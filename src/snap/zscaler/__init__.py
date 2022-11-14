import click
from pyzscaler.zia import ZIA
from pyzscaler.zia.locations import LocationsAPI
from pyzscaler.zia.traffic import TrafficForwardingAPI

import snap.config as cfg
from snap.zscaler.copy import copy
from snap.zscaler.delete import delete
from snap.zscaler.list import list
from snap.zscaler.migrate import migrate
from snap.zscaler.options import ZS_SDWAN_OPTIONS
from snap.zscaler.show import show
from snap.zscaler.update import update


class ZS(ZIA):
    """Extend ZIA class."""

    def __init__(self):
        super(ZS, self).__init__(api_key=cfg.ZIA_API,
                                 cloud='zscloud',
                                 username=cfg.ZIA_USERNAME,
                                 password=cfg.ZIA_PASSWORD)

    @staticmethod
    def fqdn(hostname: str) -> str:
        if not hostname:
            raise ValueError("hostname not set")
        else:
            return f"{hostname}@hm.com".lower()

    @staticmethod
    def presharedkey() -> str:
        return "d2uS#DD%Gt8#8WOkOT"

    @property
    def locations(self) -> LocationsAPI:
        return LocationsAPI(self)

    @property
    def traffic(self) -> TrafficForwardingAPI:
        return TrafficForwardingAPI(self)

    def add_vpn_hmcreds(self, hostname: str):
        creds = self.traffic.get_vpn_credential(fqdn=self.fqdn(hostname))

        if creds:
            click.echo("updateing existing CREDS")
            return self.traffic.update_vpn_credential(credential_id=creds.id,
                                                      pre_shared_key=self.presharedkey(),
                                                      comments="created by SNAP")
        else:
            creds = {
                "fqdn": self.fqdn(hostname),
                "preSharedKey": self.presharedkey(),
                "type": "UFQDN",
                "comments": "created by SNAP"
            }
            click.echo(f"Adding CREDS: {creds}")
            return self.traffic._post("vpnCredentials", json=creds)

    def set_options(self, locid: str):
        """Set DNS options etc for sublocation 'other'."""
        for sub_location in self.locations.list_sub_locations(locid):
            if sub_location.name in ZS_SDWAN_OPTIONS:
                click.echo(f"adding groups to sublocation {sub_location.name}")
                sub_location.static_location_groups = ZS_SDWAN_OPTIONS[sub_location.name]
                id = sub_location.pop('id')
                self.locations.update_location(location_id=id, **sub_location)


@click.group()
@click.pass_context
def zs(ctx):
    ctx.obj = ZS()


zs.add_command(migrate)
zs.add_command(copy)
zs.add_command(list)
zs.add_command(delete)
zs.add_command(show)
zs.add_command(update)

if __name__ == "__main__":
    zs()
