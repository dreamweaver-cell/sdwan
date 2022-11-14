#!/usr/bin/env bash

if [ -z "$1" ]
then
  echo "MUST GIVE HOSTNAME AS ARGUMENT"
  exit 1
fi
HOSTNAME=$1

function failed() {
  echo "FAILED: ${1} for ${HOSTNAME}";
  ansible-playbook -i inventory --limit "${HOSTNAME}" notify_play.yml -e color="EE0000" -e "msg='Premigration failed on ${1}'";
  exit 1;
}

ansible-playbook -i inventory --limit "${HOSTNAME}" ios_rommon.yml || { failed "version check failed"; }

ansible-playbook -i inventory --limit "${HOSTNAME}" notify_play.yml -e "msg='Premigration started'";

# Upgrade IOS
ansible-playbook -i inventory --limit "${HOSTNAME}" ios_backupconf.yml || { failed "backup config"; }

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

# Upgrade IOS
ansible-playbook -i inventory --limit "${HOSTNAME}" ios_upgrade.yml || { failed "ios_upgrade"; }

# Get bootstrap file
ansible-playbook -i inventory --limit "${HOSTNAME}"  get_minibootstrap.yml || { failed "bootstrap stage"; }
ansible-playbook -i inventory --limit "${HOSTNAME}" notify_play.yml -e color="00EE00" -e "msg='Premigration completed. Ready to migrate!'";
