#!/bin/bash

set -xe

export CLUSTER_PROVIDER=$TARGET

source cluster/common.sh

# Ansible tweaks/settings
export PATH=$HOME/.local/bin:$PATH
export K8S_AUTH_KUBECONFIG="$KUBE_CFG"

# Make sure that the VM is properly shut down on exit
trap '{ set +e; ansible --version; _kubectl get pvc -o yaml; _kubectl get vmis -o yaml; _kubectl get vms -o yaml; _kubectl get pods --all-namespaces; make cluster-down; }' EXIT SIGINT SIGTERM SIGSTOP

make cluster-down
make cluster-up
make cluster-sync

# Deps
pip3 install --user pyasn1 pyopenssl openshift
pip3 install --user -r requirements-dev.txt

# STABLE ansible
pip3 install --user ansible

ansible-playbook --version
ansible-playbook -vvv tests/playbooks/all.yml

sleep 30

# DEV ansible
pip3 uninstall -y ansible
pip3 install --user git+https://github.com/ansible/ansible.git

# First make sure everything has been cleaned up
objcount=$( for kind in vmi pvc vm vmirs; do _kubectl get $kind -o name; done | wc -l )
if [ $objcount != 0 ]; then
  echo "Playbooks did not clean up after themselves; aborting"
  exit 1
fi

# And another one
ansible-playbook --version
ansible-playbook -vvv tests/playbooks/all.yml
