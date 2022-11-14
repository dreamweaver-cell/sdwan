import os
from sys import path

zed = os.path.dirname(os.path.abspath(__file__))
if zed not in path:
    path.append(zed)

# TEXTFSM VARIABLES
os.environ["NET_TEXTFSM"] = f"{zed}/../snap/ntc-templates/templates"

zeddir = os.path.dirname(os.path.abspath(__file__))
