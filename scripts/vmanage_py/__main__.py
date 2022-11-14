import os

import click
import requests
import tabulate
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from vmanage_authentication import Authentication

from snap.logger import log

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

vmanage_host = os.environ.get("VMANAGE_HOST")
vmanage_username = os.environ.get("VMANAGE_USERNAME")
vmanage_password = os.environ.get("VMANAGE_PASSWORD")
vmanage_port = "443"


@click.group()
def cli():
    """Command line tool for getting information from SD-WAN.
    """


@click.command()
def device_list():
    """Retrieve and return network devices list.
        Returns information about each device that is part of the fabric.
        Example command:
            ./snap device_list
    """
    click.secho("Retrieving the devices.")

    url = base_url + "/device"

    response = requests.get(url=url, headers=header, verify=False)
    if response.status_code == 200:
        items = response.json()['data']
    else:
        print("Failed to get list of devices " + str(response.text))
        exit()

    headers = [
        "Host-Name", "Device Type", "Device ID", "System IP", "Site ID", "Version", "Device Model"
    ]
    table = list()

    for item in items:
        tr = [
            item['host-name'], item['device-type'], item['uuid'], item['system-ip'],
            item['site-id'], item['version'], item['device-model']
        ]
        table.append(tr)
    try:
        click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
    except UnicodeEncodeError:
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))


@click.command()
@click.option("--template",
              required=False,
              default="",
              help="Name of the template you wish to retrieve information for")
def template_list(template):
    """Retrieve and return templates list.
        Returns the templates available on the vManage instance.
        Example command:
            ./sdwan.py template_list
    """
    click.secho("Retrieving the templates available.")

    url = base_url + "/template/device"

    response = requests.get(url=url, headers=header, verify=False)
    if response.status_code == 200:
        items = response.json()['data']
    else:
        print("Failed to get list of templates")
        exit()
    headers = [
        "Template Name", "Device Type", "Template ID", "Attached devices", "Template version"
    ]
    table = list()

    if template != "":
        tr = [[
            item['templateName'], item['deviceType'], item['templateId'], item['devicesAttached'],
            item['templateAttached']
        ] for item in items if template in item['templateName']]
        try:
            tr = tr[0]
            table.append(tr)

        except IndexError:
            log.error(f"No Host named {template}\n")
            exit(1)

    else:
        for item in items:
            tr = [
                item['templateName'], item['deviceType'], item['templateId'],
                item['devicesAttached'], item['templateAttached']
            ]
            table.append(tr)

    try:
        click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))

    except UnicodeEncodeError:
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))


cli.add_command(device_list)
cli.add_command(template_list)

if __name__ == "__main__":
    Auth = Authentication()
    jsessionid = Auth.get_jsessionid(vmanage_host, vmanage_port, vmanage_username,
                                     vmanage_password)
    token = Auth.get_token(vmanage_host, vmanage_port, jsessionid)

    if token is not None:
        header = {'Content-Type': "application/json", 'Cookie': jsessionid, 'X-XSRF-TOKEN': token}
    else:
        header = {'Content-Type': "application/json", 'Cookie': jsessionid}

    base_url = f"https://{vmanage_host}:{vmanage_port}/dataservice"
    cli()
