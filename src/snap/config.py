"""
All configuration/definitions here.. static variables etc
"""
import os

from dotenv import load_dotenv

from snap import snapdir

load_dotenv()
DATA_DIR = os.getenv("DATA_DIR", snapdir + "/../../data")
LOG_DIR = os.getenv("LOG_DIR", snapdir + "/../../logs")
SNAPCONF_DIR = os.getenv("SNAPCONF_DIR", DATA_DIR + "/snapconfig")
SWIXCONF_DIR = os.getenv("SWIXCONF_DIR", snapdir + "/../../swixconfig")
ANSIBLE_INVENTORY = os.getenv("ANSIBLE_INVENTORY", snapdir + "/../../ansible/inventory")
ANSIBLE_FILES = os.getenv("ANSIBLE_FILES", ANSIBLE_INVENTORY + "/../files")
JSON_DEVICE_CONFIG_SCHEMA = snapdir + "/schemas/device_configuration_file.json"
JSON_DEVICE_TEMPLATE = snapdir + "/schemas/device_template.json"
SERVICES_DIR = snapdir + "/services"
SNAPSHOT_DIR = DATA_DIR + "/snapshot"
# NET_TEXTFSM = f"{snapdir}/ntc-templates/templates"
# os.environ["NET_TEXTFSM"] = f"{NET_TEXTFSM}"

LOGLEVEL = "DEBUG"
LOGFILE = "snap.log"
LOGFILE_SIZE = 150000  # bytes

DB_NAME = "cisco-sdwan-table"
DB_ENDPOINT = "https://cisco-sdwan-table.table.cosmos.azure.com:443/"

# Environment variables required
PRIME_HOST = os.getenv("PRIME_HOST", "")
DB_KEY = os.getenv("DB_KEY", "")

TACACS_USERNAME = os.getenv("TACACS_USERNAME", "")
TACACS_PASSWORD = os.getenv("TACACS_PASSWORD", "")
VMANAGE_HOST = os.getenv("VMANAGE_HOST", "")

# VPN10 variables
MAX_STATIC_ROUTES = 5

# Zscaler API
ZIA_USERNAME = os.getenv("ZIA_USERNAME", "")
ZIA_PASSWORD = os.getenv("ZIA_PASSWORD", "")
ZIA_API = os.getenv("ZIA_API", "")

# Geo API
API_GEO_KEY = "1d6d6d497dc56a2640359ad76a44e6de"
API_GEO_URL = "http://api.positionstack.com/"
API_GEO_QUR = "&query="

# Keys to ignore in comparing devicetemplates
DIFF_DEV_IGNORE = ['securityPolicyId', 'attached_devices', 'input']
