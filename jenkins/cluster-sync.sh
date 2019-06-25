#!/usr/bin/env bash

set -xe

KUBEVIRT_VER=$(curl -s https://github.com/kubevirt/kubevirt/releases/latest | grep -o "v[0-9]\.[0-9]*\.[0-9]*")
CDI_VER=$(curl -s https://github.com/kubevirt/containerized-data-importer/releases/latest | grep -o "v[0-9]\.[0-9]*\.[0-9]*")
cluster-up/kubectl.sh apply -f https://github.com/kubevirt/containerized-data-importer/releases/download/$CDI_VER/cdi-operator.yaml
cluster-up/kubectl.sh apply -f https://github.com/kubevirt/containerized-data-importer/releases/download/$CDI_VER/cdi-operator-cr.yaml

cluster-up/kubectl.sh apply -f https://github.com/kubevirt/kubevirt/releases/download/$KUBEVIRT_VER/kubevirt-operator.yaml
cluster-up/kubectl.sh create configmap -n kubevirt kubevirt-config --from-literal feature-gates=DataVolumes
cluster-up/kubectl.sh apply -f https://github.com/kubevirt/kubevirt/releases/download/$KUBEVIRT_VER/kubevirt-cr.yaml


(
  cluster-up/kubectl.sh wait --timeout=240s --for=condition=Ready -n kubevirt kv/kubevirt ;
) || {
  echo "Something went wrong"
  cluster-up/kubectl.sh describe -n kubevirt kv/kubevirt
  cluster-up/kubectl.sh describe pods -n kubevirt
  exit 1
}

sleep 12

cluster-up/kubectl.sh describe nodes

