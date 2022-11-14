"""Define the voice-service"""

from typing import Optional

# import snap.config as conf
from snap.logger import log
from snap.service import Service
from snap.viptela import SnapFeatureTemplates


class Serviceoffice_voice(Service):
    """vlan 11 is used as a Office Facility network."""

    name = "office_voice"
    provision_order = 320

    def create_clitemplate(self, device_variables: dict, device_template: dict) -> Optional[dict]:
        templatename = f"PROD-EDGE-CLI-VOICE-{ device_variables['device_name'] }".upper()
        gt = device_template.get("generalTemplates", [])
        source = [t['templateName'] for t in gt if t['templateType'] == "cli-template"]
        ft = SnapFeatureTemplates()

        clitemplate = ft.get_feature_template_dict(name_list=[templatename])
        if clitemplate:
            log.info(f"{templatename} in vmanage")
            ft._auth.close()
            return clitemplate

        log.info(f"adding {templatename} to vmanage")
        if source:
            voicetemplate = ft.get_feature_template_dict(name_list=source)
            voicetemplate = voicetemplate.get(source[0])
        else:
            voicetemplate = ft.get_feature_template_dict(name_list='PROD-EDGE-CLI-CONFIG')
            voicetemplate = voicetemplate.get('PROD-EDGE-CLI-CONFIG')
            voicetemplate['templateDefinition']['config']['vipValue'] = "! voicetemplate"

        del voicetemplate['templateId']
        voicetemplate['templateDescription'] = "SNAP generated CLI template"
        voicetemplate['templateName'] = templatename
        ret = ft.add_feature_template(voicetemplate)
        ft._auth.close()
        if not ret['status_code'] == 200:
            log.error("Unexpected response when createing voice-template")
            print(ret)
        else:
            log.info(f"{templatename} added ok")
            return ret

    def service_logic(self, device_variables: dict, device_template: dict):
        """Function called before updateing templates. All service logic goes here."""
        self.create_clitemplate(device_variables, device_template)

        # Remove all cli-template...there can only be one!
        self.remove_from_generalTemplates(key="templateType",
                                          value="cli-template",
                                          device_template=device_template)

    def update_device_template(self, device_conf: dict, device_template: dict) -> dict:
        """update device template with Office Office Printer."""
        self.template = self._render_template_file(device_conf)
        return self.merge_generalTemplates(self.template, device_template)
