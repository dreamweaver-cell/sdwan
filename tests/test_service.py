from pyclbr import Function

from snap.service import Service
from tests.helper import d4k_zs, loadservices, vars_from_file

device_vars = vars_from_file("snapconf_1k.json")
head = {"generalTemplates": [{"templateName": "name", "subTemplates": [{"subTemp": ""}]}]}
head2 = {"generalTemplates": [{"templateName": "PROD-LOGGING", "subTemplates": [{"subTemp": ""}]}]}

s = Service("base")


def test_read_template_file():
    result = s._read_template_file(filename="template.j2")
    assert str(type(result)) == "<class 'jinja2.environment.Template'>"


def test_merge_generalTemplates(d4k_zs: Function): # noqa
    d = loadservices(d4k_zs)
    s.merge_generalTemplates(head, d.device_template)
    assert {"templateName": "name", "subTemplates": [{"subTemp": ""}]
            } in d.device_template["generalTemplates"]


def test_merge_generalTemplates_2(d4k_zs: Function): # noqa
    d = loadservices(d4k_zs)
    s.merge_generalTemplates(head2, d.device_template)
    assert {"templateName": "PROD-LOGGING", "subTemplates": [{"subTemp": ""}]
            } in d.device_template["generalTemplates"]


def test_remove_from_generalTemplates(d4k_zs: Function): # noqa
    d = loadservices(d4k_zs)
    tname = d.device_template["generalTemplates"][0]["templateName"]
    s.remove_from_generalTemplates('templateName', 'PROD-AAA-EMEA', d.device_template)
    assert d.device_template["generalTemplates"][0]["templateName"] not in tname


def test_add_subtemplate(d4k_zs: Function): # noqa
    d = loadservices(d4k_zs)
    result = s.add_subtemplate([{"subTemp": "added_subtemp"}], "PROD-AAA-EMEA", d.device_template)
    assert {'subTemp': 'added_subtemp'} in result["generalTemplates"][0]["subTemplates"]
