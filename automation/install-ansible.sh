#!/bin/bash

set -xe

pip3 install --user openshift

if [ "$1" == "pip" ]; then
  pip3 install --user ansible
elif [[ "$1" =~ branch/..* ]]; then
  branch="$(echo $1|cut -d/ -f 2)"
  pip3 install --user "git+https://github.com/ansible/ansible.git@$branch"
elif [[ "$1" =~ pr/..* ]]; then
  pr="$(echo $1|cut -d/ -f 2)"
  pip3 install --user git+https://github.com/ansible/ansible.git@refs/pull/$pr/head
else
  echo "No known ansible source provided, aborting"
  exit 1
fi
