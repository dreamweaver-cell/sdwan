import click


@click.command('list')
@click.argument("locationname")
@click.pass_obj
def list(zs, locationname: str):
    """List locations in ZS-portal based on searchname"""

    locs = zs.locations.list_locations(search=locationname)
    for loc in locs:
        click.echo(f"{loc.id:<15}{loc.name}")
