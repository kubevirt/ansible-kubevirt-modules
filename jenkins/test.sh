#!/bin/bash

set -xe

export KUBEVIRT_PROVIDER=$TARGET
export KUBEVIRT_NUM_NODES=2
export KUBECONFIG=$(cluster-up/kubeconfig.sh)
export K8S_AUTH_KUBECONFIG="$KUBECONFIG"
LATEST_KUBEVIRT_VER=$(curl -s https://github.com/kubevirt/kubevirt/releases/latest | grep -o "v[0-9]\.[0-9]*\.[0-9]*")
LATEST_CDI_VER=$(curl -s https://github.com/kubevirt/containerized-data-importer/releases/latest | grep -o "v[0-9]\.[0-9]*\.[0-9]*")

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

export CDI_VER=${CDI_VER:-$LATEST_CDI_VER}
export KUBEVIRT_VER=${KUBEVIRT_VER:-$LATEST_KUBEVIRT_VER}

# Overrides
export KUBEVIRT_VER=v0.19.0   # 0.19.x is the last kubevirt that supports openshift3

# Set up the cluster
cluster-up/down.sh
cluster-up/up.sh
jenkins/cluster-sync.sh

# Run the tests
echo -e "########################################################" \
      "\n################### RUNNING TESTS ######################" \
      "\n########################################################"
bats/bin/bats jenkins/tests.bats
