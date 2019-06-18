#!/bin/bash

set -xe

export CLUSTER_PROVIDER=$TARGET
source cluster/common.sh

# Ansible tweaks/settings
export PATH=$HOME/.local/bin:$PATH
export K8S_AUTH_KUBECONFIG="$KUBE_CFG"

# Setup Python
pip3 install --user virtualenv
virtualenv py3env
source py3env/bin/activate

# Setup bats
rm -rf bats-core bats
git clone https://github.com/bats-core/bats-core.git
mkdir bats
( cd bats-core; git reset --hard 8789f910812afbf6b87dd371ee5ae30592f1423f; ./install.sh ../bats  )

# Gather debug info and shut down the cluster on exit
trap '{ set +e; ansible --version; _kubectl get pvc -o yaml; _kubectl get vmis -o yaml; _kubectl get vms -o yaml; _kubectl get pods --all-namespaces; make cluster-down; }' EXIT SIGINT SIGTERM SIGSTOP

# Set up the cluster
make cluster-down
make cluster-up
make cluster-sync

# Run the tests
echo -e "########################################################" \
      "\n################### RUNNING TESTS ######################" \
      "\n########################################################"
bats/bin/bats jenkins/tests.bats
