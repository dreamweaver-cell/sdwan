#!/usr/bin/env bash

if [ -z "$1" ]
then
  echo "MUST GIVE SITENAME AS ARGUMENT (eg nlamsso1)"
  exit 1
fi
if [[ $1 == *"rtr00"* ]]; then
  echo "MUST GIVE SITENAME AS ARGUMENT NOT ROUTERNAME (eg nlamsso1)"
  exit 1
fi

SITE=$1
PRIMARY=${SITE}rtr001
SECONDARY=${SITE}rtr002

echo "Will run premigration for ${PRIMARY} and ${SECONDARY}. Press Enter to continue."
read foo
if [[ ${foo} == *"n"* ]]; then
  exit 1
fi

function failed() {
  echo "FAILED: ${1}";
  exit 1;
}

# Run collection script
zed --device ${PRIMARY} || { failed "zed"; }
zed --device ${SECONDARY} || { failed "zed"; }

# Run Provisioning script
snap ${PRIMARY} || { failed "snap"; }
snap ${SECONDARY} || { failed "snap"; }

# Push device template to vManage
ansible-playbook -i inventory --limit ${PRIMARY} push_device_template_play.yml || { failed "push template for ${PRIMARY}"; }
ansible-playbook -i inventory --limit ${SECONDARY} push_device_template_play.yml || { failed "push template for ${SECONDARY}"; }


# Attach tempalte to device
snap  --attach ${PRIMARY} || { failed "snap-attach"; }
snap  --attach ${SECONDARY} || { failed "snap-attach"; }
