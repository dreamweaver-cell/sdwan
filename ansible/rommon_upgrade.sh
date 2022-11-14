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
CHANGE_VARS="rommon_cr_vars.yml"
ansible-playbook -i inventory --limit $HOSTNAME rommon_upgrade.yml -e $CHANGE_VARS -vvv || { failed "rommon upgraed failed"; }
