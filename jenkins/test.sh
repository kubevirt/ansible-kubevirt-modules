#!/bin/bash

set -xe

export CLUSTER_PROVIDER=$TARGET

source cluster/common.sh

# Ansible tweaks/settings
export PATH=$HOME/.local/bin:$PATH
export K8S_AUTH_KUBECONFIG="$KUBE_CFG"

pip3 install --user virtualenv
virtualenv py3env
source py3env/bin/activate

# Make sure that the VM is properly shut down on exit
trap '{ set +e; ansible --version; _kubectl get pvc -o yaml; _kubectl get vmis -o yaml; _kubectl get vms -o yaml; _kubectl get pods --all-namespaces; make cluster-down; }' EXIT SIGINT SIGTERM SIGSTOP

make cluster-down
make cluster-up
make cluster-sync

for ANSIBLE_SOURCE in pip branch/stable-2.8 branch/devel; do
  # Clean up and wait a bit
  pip uninstall -y ansible || :
  sleep 60

  # First make sure everything has been cleaned up
  objcount=$( for kind in vmi pvc vm vmirs vmipreset; do _kubectl get $kind -o name || :; done | wc -l )
  if [ $objcount != 0 ]; then
    echo "Playbooks did not clean up after themselves; aborting"
    exit 1
  fi

  # Test
  ci-common/install-ansible.sh $ANSIBLE_SOURCE

  ansible-playbook --version
  ansible-playbook -vvv tests/playbooks/all.yml
done
