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

pip3 install --user pyasn1 pyopenssl openshift
pip3 install --user git+https://github.com/ansible/ansible.git
pip3 install --user -r requirements-dev.txt

ansible-playbook --version
ansible-playbook -vvv tests/playbooks/all.yml

