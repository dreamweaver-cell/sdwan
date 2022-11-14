from datetime import date

import yaml
from nested_lookup import nested_delete, nested_lookup

from ansible.module_utils.basic import AnsibleModule
from snap.config import LOG_DIR, SNAPCONF_DIR
from snap.device import Device
from snap.logger import log, log_init


def main():
    fields = {
        "hostname": {
            "required": True,
            "type": "str"
        },
        "log": {
            "type": bool
        },
        "exclude_loopback": {
            "type": "bool",
            "default": False
        }
    }
    exclude_loopback = False
    module = AnsibleModule(argument_spec=fields)
    device = Device()
    device.load_snapfile(f"{SNAPCONF_DIR}/{module.params['hostname']}.json")
    diff = device.diff_config("vmanage")
    result_dic = {
        'changes': False,
        'diff_vars': None,
        'diff_removed': None,
        'diff_changed': {
            'new': None,
            'old': None
        }
    }

    def remove_ip_sec_tunnels(clean_dict) -> dict:
        # Remove all IPsec tunnel changs from diff file
        clean_dict = nested_delete(clean_dict, "ipsec_tunnel50_destination_ip")
        clean_dict = nested_delete(clean_dict, "ipsec_tunnel50_remote_id")
        clean_dict = nested_delete(clean_dict, "ipsec_tunnel51_destination_ip")
        clean_dict = nested_delete(clean_dict, "ipsec_tunnel51_remote_id")
        return clean_dict

    def check_if_diffs(check_dict):
        # Check if any changes left after Tunnel deletion
        if check_dict['diff_changed']['new'] or check_dict['diff_changed']['old'] or check_dict[
                'diff_removed'] or check_dict['diff_vars']:
            return True

    if diff:
        result_dic['diff_changed']['new'] = nested_lookup("new_value",
                                                          diff[0].get("values_changed"))
        result_dic['diff_changed']['old'] = nested_lookup("old_value",
                                                          diff[0].get("values_changed"))
        result_dic['diff_removed'] = nested_lookup("templateName",
                                                   diff[0].get("iterable_item_removed"))
        if len(diff) > 1:
            result_dic['diff_vars'] = diff[1]

        if not result_dic['diff_changed']['new'] and not result_dic['diff_changed'][
                'old'] and not result_dic['diff_removed']:
            result_dic['diff_vars'] = diff[0]

    if exclude_loopback:
        result_dic = remove_ip_sec_tunnels(result_dic)

    if check_if_diffs(result_dic):
        result_dic['changes'] = True

    output = result_dic
    if log and result_dic['changes']:
        dump_host_var_to_yaml(module.params['hostname'], yaml.dump(output))
    module.exit_json(changed=False, meta=output, diff=bool(result_dic['changes']))


def dump_host_var_to_yaml(hostname, data_obj):
    ''' Saving file to differ log directory'''
    print("CONF", LOG_DIR + "/diffs/" + hostname)
    with open(f"{LOG_DIR}/diffs/{hostname}.yml", "w") as file:
        file.write(data_obj)


if __name__ == '__main__':
    main()
