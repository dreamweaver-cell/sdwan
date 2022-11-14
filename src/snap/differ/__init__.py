import os
from sys import path

differ = os.path.dirname(os.path.abspath(__file__))
if differ not in path:
    path.append(differ)
