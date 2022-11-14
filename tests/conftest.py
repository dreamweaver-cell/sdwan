"""tests for SNAP."""

import json
import os
import pickle

import pytest
from azure.cosmosdb.table.models import Entity
from box import Box
from hmnet import netdb
from vmanage.api.authentication import Authentication
from vmanage.api.http_methods import HttpMethods
from vmanage.data.template_data import TemplateData

from snap import services
from snap.services.office_voice import Serviceoffice_voice
from snap.viptela import SnapDeviceTemplates

mypath = os.path.dirname(__file__)


def get_zs_return_value(ip: str) -> dict:
    return Box({
        'primaryIp': '165.225.114.30',
        'primaryMeta': {
            'region': 'Oceania',
            'country': 'Australia',
            'city': 'Sydney',
            'dcName': 'SYD3',
            'latitude': -34.0,
            'longitude': 152.0
        },
        'secondaryIp': '165.225.226.48',
        'secondaryMeta': {
            'region': 'Oceania',
            'country': 'Australia',
            'city': 'Melbourne',
            'dcName': 'MEL2',
            'latitude': -37.0,
            'longitude': 145.0
        },
        'tertiaryIp': '165.225.112.30',
        'tertiaryMeta': {
            'region': 'Asia',
            'country': 'Singapore',
            'city': 'Singapore',
            'dcName': 'SIN4',
            'latitude': 2.0,
            'longitude': 103.0
        }
    })


@pytest.fixture(autouse=True)
def mock_zsdestination(monkeypatch):
    monkeypatch.setattr(services.zscaler_ipsec, "get_zsdestinations", get_zs_return_value)


def siteentry(*args) -> dict:
    """Mocked get_first function."""
    s = Entity()
    s.sitetable = "sitecode"
    if "ausydso1" in args[1]:
        s.RowKey = "01"
        s.PartitionKey = "306105"
        s.sitename = "ausydso1"
        s.region = "apac"
    else:
        s.RowKey = "99"
        s.PartitionKey = "104699"
        s.sitename = "sesthxx3"
        s.region = "emea"
    return s


@pytest.fixture(autouse=True)
def mock_netdbaccess(monkeypatch):
    """Patches netdb.get_first for all tests."""
    monkeypatch.setattr(netdb, "get_first", siteentry)


def clitemplate(self, device_variables, device_template) -> dict:
    return {'PROD-EDGE-CLI-VOICE-DEHAMSO1RTR001': {}}


@pytest.fixture(autouse=True)
def mock_vmanageaccess(monkeypatch):
    """Patches office_vocie.create_clitemplate"""
    monkeypatch.setattr(Serviceoffice_voice, "create_clitemplate", clitemplate)


def response(self, method, headers=None, payload=None, files=None, timeout=10) -> dict:
    with open(f"{mypath}/support/http_response.obj", "rb") as f:
        response = pickle.load(f)
    return response


@pytest.fixture(autouse=True)
def mock_http_methods_response(monkeypatch):
    """Patches http_methods.response"""
    monkeypatch.setattr(HttpMethods, "request", response)


def login_session(self) -> dict:
    with open(f"{mypath}/support/vmanage_login.obj", 'rb') as f:
        session_obj = pickle.load(f)
    return session_obj


@pytest.fixture(autouse=True)
def mock_vmanageauthentication(monkeypatch):
    """Patches authentication.login"""
    monkeypatch.setattr(Authentication, "login", login_session)


def device_tmpl_list(self, factory_default=False, name_list=None) -> dict:
    with open(f"{mypath}/support/device_tmpl_list.json", 'rb') as f:
        return_list = json.load(f)
    return return_list


@pytest.fixture(autouse=True)
def mock_template_data(monkeypatch):
    """Patches template_data.export_device_template_list"""
    monkeypatch.setattr(TemplateData, "export_device_template_list", device_tmpl_list)


def get_temp_input(self, template_id, device_id_list=None) -> dict:
    with open(f"{mypath}/support/template_input.json", "r") as f:
        temp = json.load(f)
    return temp


@pytest.fixture(autouse=True)
def mock_get_template_input(monkeypatch):
    """Patches template_data.export_device_template_list"""
    monkeypatch.setattr(SnapDeviceTemplates, "get_template_input", get_temp_input)
