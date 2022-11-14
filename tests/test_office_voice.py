from pyclbr import Function
from typing import Tuple

import pytest

from snap.service import Service
from tests.helper import d4k_voice, loadservices

service = Service(name="office_voice")


@pytest.fixture(autouse=True)
def device_conf_d4k_voice(d4k_voice: Function) -> tuple:  # noqa: F811
    d = loadservices(d4k_voice)
    var = d.device_variables
    temp = d.device_template
    return var, temp


def test_create_clitemplate(device_conf_d4k_voice: tuple):
    device_variables, device_templates = device_conf_d4k_voice
    ret = service.create_clitemplate(device_variables, device_templates)
    assert ret == {'PROD-EDGE-CLI-VOICE-DEHAMSO1RTR001': {}}
