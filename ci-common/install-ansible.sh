#!/bin/bash

set -xe

pip install openshift

if [[ "$1" == "pip" ]]; then
  pip install ansible
elif [[ "$1" =~ branch/..* ]]; then
  branch="$(echo $1|cut -d/ -f 2)"
  pip install "git+https://github.com/ansible/ansible.git@$branch"
elif [[ "$1" =~ pr/..* ]]; then
  pr="$(echo $1|cut -d/ -f 2)"
  pip install git+https://github.com/ansible/ansible.git@refs/pull/$pr/head
else
  echo "No known ansible source provided, aborting"
  exit 1
fi
