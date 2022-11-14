"""Customize this to run a function of your need."""
import click


def print_loc(zs, loc):
    click.echo(f"location name: {loc.name}")


def check_lan(zs, loc):
    click.echo("location, sublocation, SurrogateIP, SurrogateEnforce")
    subs = zs.locations.list_sub_locations(location_id=loc.id)
    for sub in subs:
        if "lan" in sub.name.lower():
            if not (sub.surrogate_ip and sub.surrogate_ip_enforced_for_known_browsers):
                click.echo(f"{loc.name} {sub.name} {sub.surrogate_ip} \
                      {sub.surrogate_ip_enforced_for_known_browsers} {sub.idle_time_in_minutes} \
                      {sub.surrogate_refresh_time_in_minutes}")
                id = sub.pop('id')
                sub.surrogate_ip = True
                sub.surrogate_ip_enforced_for_known_browsers = True
                zs.locations.update_location(location_id=id, **sub)


@click.command('update')
@click.argument("locationname")
@click.option('--funcname',
              '-f',
              default="print_loc",
              help='Function to be applied',
              show_default=True)  # noqa
@click.pass_obj
def update(zs, locationname: str, funcname: str):
    """Custom command to update a location with correct settings."""

    locs = zs.locations.list_locations(search=locationname)
    func = globals().get(funcname)
    if func == "print_loc":
        click.echo("DEFAULT function print_loc used. Will only print the location.")
    for loc in locs:
        # check_lan(zs, loc)
        func(zs, loc)
    zs.config.activate()
