"""Initialize services"""
from snap.service import Service  # noqa

from .base import ServiceBase  # noqa
from .capwap import Servicecapwap  # noqa
from .dc_gwms import Servicedc_gwms  # noqa
from .dual_router import Servicedual_router  # noqa
from .firewall import ServiceFirewall  # noqa
from .head import ServiceHead  # noqa
from .internet import Serviceinternet  # noqa
from .lan import ServiceLan  # noqa
from .manual import ServiceManual  # noqa
from .office_atea_screen import Serviceoffice_atea_screen  # noqa
from .office_compute import Serviceoffice_compute  # noqa
from .office_ds_switch_ospfv3 import Serviceoffice_ds_switch_ospfv3  # noqa
from .office_facility import Serviceoffice_facility  # noqa
from .office_flowscape import Servceoffice_flowscape  # noqa
from .office_hm_wifi_data import Serviceoffice_hm_wifi_data  # noqa
from .office_ospf import Serviceoffice_ospf  # noqa
from .office_printer import Serviceoffice_printer  # noqa
from .office_provisioning import Serviceoffice_provisioning  # noqa
from .office_thin_clients import Serviceoffice_thin_clients  # noqa
from .office_voice import Serviceoffice_voice  # noqa
from .sbc_telephony import ServiceSbcTelephony  # noqa
from .vlan315_security_camera import Servicevlan315_security_camera  # noqa
from .vlan332_external_partners import Servicevlan332_external_partners  # noqa
from .vpls import ServiceVpls  # noqa
from .zscaler import ServiceZscaler  # noqa
from .zscaler_ipsec import ServiceZscalerIpsec  # noqa
from .zscaler_pop import ServiceZscaler_pop  # noqa
