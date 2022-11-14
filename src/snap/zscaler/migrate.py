"""Trigger migration from gre->ipsec in ZS-portal."""
import click

from snap.logger import log


@click.command()
@click.argument("hostname", required=True, default=None)
@click.pass_obj
def migrate(zs, hostname: str):
    """Migrates a location from GRE to IPSEC in ZS-portal."""
    loc = zs.locations.get_location(location_name=hostname)
    if not loc:
        log.error("location name not found")
        exit(1)

    cred = zs.add_vpn_hmcreds(hostname)
    payload = {'vpn_credentials': [cred], 'name': hostname, 'ip_addresses': []}
    # bug in snake_to_camel ...
    payload['surrogateIP'] = True
    payload['surrogateIPEnforcedForKnownBrowsers'] = True
    # update existing location with IPsec credentials and remote static tunnels
    zs.set_options(loc.id)
    click.echo(zs.locations.update_location(loc.id, **payload))
    zs.config.activate()
