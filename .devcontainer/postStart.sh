#!/bin/bash

PKGS=(.)

for PKG in "${PKGS[@]}"
do
    if [ -d "${PKG}" ]; then
        pip3 install -e "${PKG}"
    fi
done

ansible-galaxy install -r ./ansible/requirements.yml
