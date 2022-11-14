import os
from sys import path

import hmnet.hmnor as hmnor

hmnor = os.path.dirname(os.path.abspath(hmnor.__file__))
if hmnor not in path:
    path.append(hmnor)

# TEXTFSM VARIABLES
os.environ["NET_TEXTFSM"] = f"{hmnor}/ntc-templates/templates"


class HmnorConfigError(Exception):
    """Some problem with the config definition for this host"""
    pass
