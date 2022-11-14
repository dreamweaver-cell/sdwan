import json

import click


@click.command('show')
@click.argument("locationname")
@click.pass_obj
def show(zs, locationname: str):
    """Show info of given location."""

    loc = zs.locations.get_location(location_name=locationname)
    if loc:
        click.echo(json.dumps(loc))
    else:
        click.secho(f"{locationname} not found in portal", fg='red')
