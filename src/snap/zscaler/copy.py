"""Copies one location to another in ZS-portal."""

import click
from pyzscaler.utils import snake_to_camel


@click.command()
@click.argument("source", required=True, default=None)
@click.argument("destination", required=True, default=None)
@click.pass_obj
def copy(zs, source: str, destination: list):
    """Copies locationname from source to desitnation and sets it up with VPN-credentials."""

    src = zs.locations.get_location(location_name=source)
    if not src:
        click.secho(f"source location name {source} not found", fg='red')
        exit(1)

    dst = zs.locations.get_location(location_name=destination)
    if dst:
        click.secho(f"destination location name {destination} already exists", fg='red')
        exit(1)

    click.echo(f"location found: {src.name} {src.id}")
    new = src.copy()
    del (new.id)
    del (new.name)

    # Bug i snake_to_camel, så måste skapa payloaden här skjuta med post.
    payload = {"name": destination}
    for key, value in new.items():
        payload[snake_to_camel(key)] = value
    cred = zs.add_vpn_hmcreds(destination)
    click.echo(f"VPN-credentials: {cred.fqdn} {cred.id}")

    payload['vpnCredentials'] = [cred]
    payload['ipAddresses'] = []

    # Create the new location
    loc = zs.locations._post("locations", json=payload)

    # Copy sublocations
    subs = zs.locations.list_sub_locations(location_id=src.id)
    for sub in subs:
        # Group other cannot be created explicitly
        if not sub.name == "other":
            click.echo(f"adding sublocation: {sub.name}")
            sub.parent_id = loc.id
            zs.locations.add_location(**sub)

    # Set Groups for sublocation other
    zs.set_options(loc.id)

    click.secho(f"created new location: {destination} {loc.id}", fg='green')
    zs.config.activate()
