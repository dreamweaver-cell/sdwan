import ast
from pprint import pprint as pprint
from textwrap import indent

import click
import jsonschema
import simplejson as json
from dotenv import load_dotenv
from hmnet.hmnor.connect import nornir_obj
from nornir_utils.plugins.functions import print_result

import snap.config as conf
from snap.logger import log, log_init
from zed.swix import swix_module


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--host', help='device hostname')
@click.option('--commands', required=False, help='List of IOS commands')
@click.option('--command', required=False, help='Single IOS command')
@click.option('--facts', is_flag=True, default=False, required=False, help='Get Switch ISO facts')
def run(host, commands, command, facts):
    load_dotenv()
    log_init(False)

    if facts:
        commands = [
            "show version", "show cdp neighbor", "show interface switchport",
            "show interface status", "show interface vlan5"
        ]
    nr = nornir_obj(host, ios_commands=commands, debug=True, quiet=False)
    cmd = [
        str(nr.results[host][2]),
        str(nr.results[host][3]),
        str(nr.results[host][4]),
        str(nr.results[host][5]),
        str(nr.results[host][6])
    ]
    cmd_list = []

    for cmd_output in cmd:
        # print(cmd_output)
        try:
            cmd_list.append(json.loads(json.dumps(ast.literal_eval(cmd_output))))
        except SyntaxError:
            log.info("error")
    device = swix_module.device_object(cmd_list, host)

    with open(f"{conf.SWIXCONF_DIR}/{device.obj_hostname}.json", 'w') as outfile:
        json.dump(device.combined_dict, outfile, indent=4)

    log.info(f"{conf.SWIXCONF_DIR}/{device.obj_hostname}.json meta file created")
    # print(json.dumps(device.newservie, indent=4))


def main(**kwargs):
    run(**kwargs)


if __name__ == "__main__":
    #
    # Switch Collection started
    #

    log.info("Initiating Nornir")
    main()
