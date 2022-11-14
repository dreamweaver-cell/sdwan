import logging

from snap.logger import log, log_init


class VmanageDiff():
    '''
    Returns diff inforamtion between snapconfig files and vmanage
        Pareameters:
            add list(): Device templates added to vmanage
            remove list(): Device templates removed from vmanage
            change list(): Device templates changed
            variables: list(): Variables changed

        Returns:
            Dict { remove: list(): add: list(): change: list(): variables: list()}
    '''

    def __init__(self, diff: str, add: str, remove: str, change: str, hostname: str):
        """ VmanageDiff Obj Blueprint """
        self.hostname = hostname
        self.output: dict = {"add": [], "remove": [], "change": [], "variables": []}
        self.diff = diff
        self.added_device_templates = add
        self.removed_dcevice_templates = remove
        self.changed_device_templates = change
        for diff_devicetemplates in self.changed_device_templates:
            self.check_device_template_to_be_changed(diff_devicetemplates)
        try:
            for diff_removed_devicetemplates in self.removed_dcevice_templates:
                self.check_device_template_to_be_deleted(diff_removed_devicetemplates)
        except IndexError:
            pass
        try:
            for diff_added_devicetemplates in self.added_device_templates:
                self.check_device_template_to_be_added(diff_added_devicetemplates)
        except IndexError:
            pass
        try:
            for diff_changed_variables in diff[1]:
                self.check_variables_to_be_changed(diff[1], diff_changed_variables)
        except IndexError:
            pass

    def check_device_template_to_be_changed(self, devicetemplate: str):
        """Template Changed."""
        if not isinstance(devicetemplate, str):
            devicetemplate = f"{devicetemplate['templateName']}"
        log.warning("Template Changed: %s", devicetemplate)
        self.output["change"].append(devicetemplate)

    def check_device_template_to_be_deleted(self, devicetemplate_delete):
        """Templates remove."""
        log.warning("Template Deleted: %s", devicetemplate_delete)
        self.output["remove"].append(devicetemplate_delete)

    def check_device_template_to_be_added(self, devicetemplate_add):
        "Templates add."
        log.warning("Template Added: %s", devicetemplate_add)
        self.output["add"].append(devicetemplate_add)

    def check_variables_to_be_changed(self, obj, device_variables):
        """Variabled change."""
        log.warning("Variables Modified: %s", device_variables)

        self.output["variables"].append(device_variables)
