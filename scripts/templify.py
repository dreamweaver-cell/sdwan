import sys

import yaml
from jinja2 import Template
from yaml.loader import SafeLoader

import snap.config as cfg


def run():
    with open(f'{sys.argv[1]}.yml') as yml_file_:
        router_vars = yaml.load(yml_file_, Loader=SafeLoader)
    with open(f'template/isr4k.j2') as j2_file_:
        template = Template(j2_file_.read())
        print(template.render(router=router_vars))

if __name__ == '__main__':
    run()
