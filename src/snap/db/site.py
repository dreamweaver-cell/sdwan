import click
from hmnet import netdb
from hmnet.netdb import Site
from tabulate import tabulate


@click.group('site')
@click.pass_obj
def site(obj):
    """List sites in the netdb based on searchname"""


@click.command('list')
@click.argument("sitename", required=True, default="")
def lista(sitename: str = ""):
    """List sites in the netdb based on searchname."""

    for _ in netdb._get_siteid_entries():
        if sitename in _['sitename']:
            s = Site(_['sitename'])
            click.echo(f"{s.siteid} {s.sitename} {s.region}")


@click.command('add')
@click.argument("sitename", required=True, default="")
def add(sitename: str = ""):
    """Add new site to the netdb."""

    click.echo("Adding site not yet implemented")


site.add_command(lista)
site.add_command(add)
