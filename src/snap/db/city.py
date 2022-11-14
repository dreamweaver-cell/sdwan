import click
from hmnet import netdb
from tabulate import tabulate


@click.group('city')
@click.pass_obj
def city(obj):
    """List cities in the netdb based on searchname"""


@click.command('list')
@click.argument("citycode", required=False, default="")
def lista(citycode: str = ""):
    """List sites in the netdb based on searchname or all codes if no search code is entered."""

    output = [{
        "citycode": row.citycode,
        "cityid": row.cityid
    } for row in netdb.get_cities(citycode)]

    print(tabulate(output, headers='keys'))


@click.command('add')
@click.argument("citycode", required=True, default="")
def add(sitename: str = ""):
    """Add new citycode to the netdb."""

    click.echo("Adding citycode not yet implemented")


city.add_command(lista)
city.add_command(add)
