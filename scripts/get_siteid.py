from hmnet import netdb


def get_siteid(device_variables: dict) -> str:
    # checkout existing or register new site
    s = netdb.Site(device_variables["device_name"])
    device_variables["site_id"] = s.siteid
    device_variables["region"] = s.region
    return s.siteid


"""
Add configuration data:
Variable:
---------
    device_name (str): The hostname to be registered in db
    site_id (str): The site id ( if available )
    region (str): The host location (emea,amer,apac)

"""

device_variables = {"device_name": "idjakpo1rtr001", "site_id": "", "region": "emea"}

# run Play
site_id = get_siteid(device_variables)
print(site_id)
