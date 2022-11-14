#!/usr/bin/env bash


if [ -z "$1" ]
then
  echo "MUST GIVE HOSTNAME AS ARGUMENT"
  exit 1
fi
HOSTNAME=$1

function failed() {
  echo "FAILED: ${1} for $HOSTNAME";
#   ansible-playbook -i inventory --limit $HOSTNAME notify_play.yml -e color="EE0000" -e "msg='upgrade failed on ${1}'";
  exit 1;
}

ansible-playbook -i inventory --limit $HOSTNAME  -vvv ios_upgrade.yml -e upgrade_ios_version=16.09.07 || { failed "ios upgrade failed"; }
ansible-playbook -i inventory --limit $HOSTNAME  -vvv pre_upgrade.yml 
