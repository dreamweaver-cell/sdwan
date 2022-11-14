import json
from os import path
from typing import Optional

from jinja2 import Template

import snap.config as config
from snap.logger import log
from snap.utils import find_template


class Service(object):
    """Base class of services"""

    name = ''  # this is the name mapped in snapconfig-file
    provision_order = 100

    def __new__(cls, name: str):
        """factory an instance of type subclass based on name

        Args:
            name: name of service
        """
        subclass_map = {subclass.name: subclass for subclass in cls.__subclasses__()}
        try:
            subclass = subclass_map[name]
            instance = super(Service, subclass).__new__(subclass)
            return instance
        except KeyError:
            log.warning("no service definition for service: %s", name)
        else:
            return None

    def __init__(self, name: str):
        """initialize instance based on service name

        Args:
            name: name of service
        """
        self.template_dir = f"{config.SERVICES_DIR}/{self.name}/"
        self.template: dict = {}
        log.debug("init %s", self.name)

    @staticmethod
    def get_services():
        """Find children."""
        return [subclass.name for subclass in Service.__subclasses__()]

    def _add_general_templates(self, device_template, updates):
        return device_template.get("generalTemplates", []) + updates.get("generalTemplates", [])

    def _read_template_file(self, filename: str) -> Optional[dict]:
        basename = f"{self.template_dir}/{filename}"
        log.debug("loading %s", basename)
        if path.exists(basename):
            with open(basename, mode="r", encoding="utf-8") as temp:
                ret = Template(temp.read())
                return ret
        else:
            log.info("%s not found, skipping.", basename)
            return None

    def _render_template_file(self, device_conf, filename="template.j2"):
        renered = self._read_template_file(filename).render(device_conf)
        return json.loads(renered)

    def update_device_template(self, device_vars, device_template) -> dict:
        """update device template for a device."""
        self.template = self._render_template_file(device_vars)
        self.template["generalTemplates"] = self._add_general_templates(
            self.template, device_template)
        return device_template.update(self.template)

    def update_device_variables(self, device_variables: dict) -> Optional[dict]:
        """Update device variables from template-file."""
        filename = "variables.j2"
        template = self._read_template_file(filename)
        if template:
            variables = self._render_template_file(device_variables, "variables.j2")
            return device_variables.update(variables)

    def merge_generalTemplates(self, head, device_template: dict) -> None:
        """Merge head template into device_template."""
        gt = device_template.get("generalTemplates", [])
        if not head:
            return
        if not type(device_template) == type(head):
            raise TypeError("cannot merge different types")
        for t in head["generalTemplates"]:
            name = t.get("templateName")
            if not name:
                raise NameError("cannot find templateName in head")
            if find_template(name, gt):
                device_template = self.add_subtemplate(t.get("subTemplates"), name,
                                                       device_template)
            else:
                gt.append(t)

    def remove_from_generalTemplates(self, key: str, value: str, device_template: dict) -> dict:
        """remove templates from generalTemplates that match key == value."""
        gt = device_template.get("generalTemplates", [])
        for i in range(len(gt)):
            if gt[i][key] == value:
                del gt[i]
                break
        return device_template

    def add_subtemplate(self, sub: str, parentname: str, device_template: dict):
        """adding subtemplates to a parent. will not add subsubtemplates!"""
        if not sub:
            return device_template
        for parent in device_template.get("generalTemplates", []):
            if parent.get("templateName") == parentname:
                if not parent.get("subTemplates"):
                    parent["subTemplates"] = []
                parent.get("subTemplates").extend(sub)
        return device_template

    def service_logic(self, device_variables: dict, device_template: dict):
        """is run before updates in each service. Must be implemented in subclass"""
