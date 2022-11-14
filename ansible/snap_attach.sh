#!/usr/bin/env bash

light_red='\e[1;91m%s\e[0m\n'
light_green='\e[1;92m%s\e[0m\n'

if [ -z "$1" ]
then
  echo "MUST GIVE HOSTNAME and CHANGE_VARS AS ARGUMENT"
  exit 1
fi

ping -c 1 -q "$1"
if [ "$?" -eq 0 ]; then
  printf "$light_green" "[ CONNECTION AVAILABLE ]"
else
  printf "$light_red" "[ HOST DISCONNECTED ]"
  exit 0
fi

HOSTNAME=$1
snap "${HOSTNAME}"
ansible-playbook -i inventory --limit "${HOSTNAME}" snap_attach.yml || { echo "ERROR: reprovisioning failed for ${HOSTNAME}" ; exit 1; }
