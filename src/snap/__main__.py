"""
Read host information and creates sdwan device in vManage.
"""
import logging

import click

from snap.config import SNAPCONF_DIR
from snap.device import Device
from snap.logger import log, log_init


@click.group(invoke_without_command=True)
@click.argument('router', default='')
@click.option("--config-file",
              "-c",
              "conf_file",
              required=False,
              help="Specify snap-configuraiton file.",
              type=click.Path(exists=False, file_okay=True, readable=True))
@click.option("--debug/--no-debug", "-d", default=False, help="Enable / disable debug output.")
@click.option("--quiet/--no-quiet", "-q", default=False, help="Supress logoutput to stdout")
@click.option("--diff",
              "diffile",
              default='',
              required=False,
              help="Print diff config-file and vmanage. Will not write files.")
@click.option("--dry-run/--no-dry-run",
              "-n/ ",
              "_dryrun",
              is_flag=True,
              default=False,
              required=False,
              help="Dry run, don not write files to disk")
@click.option("--attach",
              is_flag=True,
              default=False,
              required=False,
              help="Push and attach template to vmanage directly")
@click.pass_context
def cli(ctx, router: str, conf_file: str, debug, quiet, diffile, _dryrun, attach):
    """initiates provisioning process"""

    log_init(debug)
    if quiet:
        log.setLevel(logging.WARN)
    if not conf_file:
        if router:
            conf_file = f"{SNAPCONF_DIR}/{router}.json"
        else:
            click.echo(ctx.get_help())
            ctx.exit()

    log.info("Reading config from: %s", conf_file)
    device = Device()
    device.load_snapfile(conf_file)

    if diffile:
        log.debug("print diff")
        vmanage_diff = device.diff_config(diffile)
        device.print_diff(vmanage_diff)

    elif _dryrun:
        device.print_device_template()
        device.print_device_variables()
        return
    else:
        log.info("writeing template and variable files")
        device.write_template_files()
        if attach:
            device.vmanage_attach()
    return


def main(**kwargs):
    """provisioning start"""
    cli(**kwargs)


if __name__ == "__main__":
    main()
