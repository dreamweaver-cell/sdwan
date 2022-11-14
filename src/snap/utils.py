from typing import Optional, Union


def find_template(name: str, lista: list, searchkey: str = 'templateName') -> list:
    """find templatename in list of templates, typically generaltemplates."""
    return [t for t in lista if t[searchkey] == name]


def get_inputdata_vars(inputdata: dict) -> Optional[dict]:
    """Remake inputdata into {var: value} """

    ret = {}
    data = inputdata.get('data')
    if data:
        for var in inputdata.get('columns'):
            ret[var['variable']] = data[0][var['property']]

    return ret


def get_vardiff(old: dict, new: dict, variables=None) -> Optional[dict]:
    """Return the dict-diffrence between old and new, comparing the keys in vars."""
    ret = {}
    if not variables:
        variables = old.keys()
    ret = {
        k: {
            'new': new.get(k, ''),
            'old': old.get(k, '')
        } for k in variables if old.get(k, '') != new.get(k, '')
    }
    return ret
