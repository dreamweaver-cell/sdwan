import click


@click.command('delete')
@click.argument("locationname")
@click.pass_obj
def delete(zs, locationname: str):
    """Delete location in ZS-portal."""

    loc = zs.locations.get_location(location_name=locationname)
    if loc:
        if click.confirm(f"This will delete {loc.name} ({loc.id}). Are you sure?"):
            zs.locations.delete_location(loc.id)
    else:
        click.secho("loc not found", fg='red')
