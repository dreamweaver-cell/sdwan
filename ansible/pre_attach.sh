#!/usr/bin/env bash

if [ -z "$1" ]
then
  echo "MUST GIVE HOSTNAME AS ARGUMENT"
  exit 1
fi
HOSTNAME=$1

function failed() {
  echo "FAILED: ${1} for ${HOSTNAME}";
  exit 1;
}

# Run collection script
zed --device ${HOSTNAME} || { failed "zed"; }

# Run Provisioning script
snap ${HOSTNAME} || { failed "snap"; }

# Push device template to vManage
ansible-playbook -i inventory --limit "${HOSTNAME}"  push_device_template_play.yml || { failed "push template"; }

# Attach tempalte to device
#ansible-playbook -i inventory --limit "${HOSTNAME}"  attach_template.yml || { failed "attach template"; }
# Attach tempalte to device using snap
echo "ATTACH template with SNAP *******"
snap --attach ${HOSTNAME} || { failed "snap-attach"; }
