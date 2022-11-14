import click
from hmnet import netdb

import snap.config as cfg
from snap.db.city import city
from snap.db.site import site


@click.group()
@click.pass_context
def db(ctx):
    ctx.obj = netdb.Site()


db.add_command(site)
db.add_command(city)

if __name__ == "__main__":
    db(None)
