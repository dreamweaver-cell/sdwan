import json
import logging
from datetime import date
from pprint import pprint as pprint

import click
from nested_lookup import nested_lookup

from snap.config import LOG_DIR, SNAPCONF_DIR
from snap.device import Device
from snap.differ.module import VmanageDiff
from snap.logger import log, log_init


@click.command()
@click.argument('router')
def cli(router):
    log_init(False)
    log.info("comparing hostname: %s to vmanage", router)
    log.setLevel(logging.WARN)
    device = Device()
    device.load_snapfile(f"{SNAPCONF_DIR}/{router}")
    diff = device.diff_config("vmanage")
    removed_dcevice_templates = []
    added_device_templates = []
    changed_device_templates = []

    if not diff:
        output = {"synchronized": str(date.today())}
    else:
        try:
            changed_device_templates = nested_lookup("new_value", diff[0].get("values_changed"))
        except AttributeError:
            pass
        try:
            removed_dcevice_templates = nested_lookup(
                "templateName", diff[0].get("iterable_item_removed"))  # noqa: E501
        except AttributeError:
            pass
        try:
            added_device_templates = nested_lookup("templateName",
                                                   diff[0].get("iterable_item_added"))
        except AttributeError:
            pass
        diff_obj = VmanageDiff(diff=diff,
                               add=added_device_templates,
                               remove=removed_dcevice_templates,
                               change=changed_device_templates,
                               hostname=router)
        print("--- dict print ---")
        pprint(diff_obj.output, indent=4)
        output = diff_obj.output

    # write to file
    dump_host_var_to_json(router, output)


def dump_host_var_to_json(hostname, data_obj):
    print("CONF", LOG_DIR + "/diffs/" + hostname)
    with open(f"{LOG_DIR}/diffs/{hostname}", "w") as file:
        json.dump(data_obj, file, indent=4)


def main(**kwargs):
    """provisioning start"""
    cli(**kwargs)


if __name__ == "__main__":
    main()
