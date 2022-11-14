#!/usr/bin/env bash

if [ -z "$1" ]
then
  echo "MUST GIVE HOSTNAME and CHANGE_VARS AS ARGUMENT"
  exit 1
fi

function failed() {
  echo "FAILED: ${1} for ${HOSTNAME}";
  exit 1;
}

echo "----- REMEMBER TO MIGRATE IN ZSCALER-PORTAL -----"
echo "Press Enter to continue"
read foo

HOSTNAME=$1
CHANGE_VARS="change_request_vars.yml"

# Delete index file
ansible-playbook -i inventory --limit "${HOSTNAME}" delete_index_file.yml || { failed "index-delete"; }

# Migration
ansible-playbook -i inventory --limit "${HOSTNAME}" migration.yml -e $CHANGE_VARS -vvv || { failed "migration failed" ; }
