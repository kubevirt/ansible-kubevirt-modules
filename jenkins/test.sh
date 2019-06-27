#!/bin/bash

set -xe

export KUBEVIRT_PROVIDER=$TARGET
export KUBEVIRT_NUM_NODES=2
export KUBECONFIG=$(cluster-up/kubeconfig.sh)
export K8S_AUTH_KUBECONFIG="$KUBECONFIG"

# Setup Python
export PATH=$HOME/.local/bin:$PATH
pip3 install --user virtualenv
virtualenv py3env
source py3env/bin/activate

# Setup bats
rm -rf bats-core bats
git clone https://github.com/bats-core/bats-core.git
mkdir bats
( cd bats-core; git reset --hard 8789f910812afbf6b87dd371ee5ae30592f1423f; ./install.sh ../bats  )

# Gather debug info and shut down the cluster on exit
trap '{ set +e; for kind in vmi pvc vm vmirs vmipreset template; do cluster-up/oc.sh get $kind -o yaml; done; cluster-up/oc.sh get pods --all-namespaces; make cluster-down; }' EXIT SIGINT SIGTERM SIGSTOP

# Set up the cluster
make cluster-down
make cluster-up
make cluster-sync

# Run the tests
echo -e "########################################################" \
      "\n################### RUNNING TESTS ######################" \
      "\n########################################################"
bats/bin/bats jenkins/tests.bats
