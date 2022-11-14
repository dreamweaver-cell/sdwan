---
#!/usr/bin/env bash

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
snap ${HOSTNAME}
ansible-playbook -i inventory --limit "${HOSTNAME}" ios_new_test.yml || { echo "ERROR: tests failed for ${HOSTNAME}" ; exit 1; }
