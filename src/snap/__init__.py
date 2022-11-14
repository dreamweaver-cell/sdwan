import os
from sys import path

snapdir = os.path.dirname(os.path.abspath(__file__))
if snapdir not in path:
    path.append(snapdir)


class SnapConfigError(Exception):
    """Some problem with the config definition for this host"""
