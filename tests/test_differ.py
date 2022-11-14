from snap.device import Device
from snap.differ.module import VmanageDiff
from tests.helper import diff_snapconfig_vmanage_output


def runtests(d: Device):
    assert d.output['add'] == ['ADD1, ADD2, ADD3']
    assert d.output['change'] == ['CHA1, CHA2, CHA3']
    assert d.output['remove'] == ['REM1', 'REM2', 'REM3']
    assert d.output['variables'] == ['foo']


def test_differ_Vmanagediff(diff_snapconfig_vmanage_output: list):  # noqa F811

    diff_list = diff_snapconfig_vmanage_output
    added_device_templates = diff_list[0]
    removed_dcevice_templates = diff_list[1]
    changed_device_templates = diff_list[2]
    diff = [[], ['foo']]
    router = 'testrouter'

    diff_obj = VmanageDiff(diff=diff,
                           add=added_device_templates,
                           remove=removed_dcevice_templates,
                           change=changed_device_templates,
                           hostname=router)
    runtests(diff_obj)
