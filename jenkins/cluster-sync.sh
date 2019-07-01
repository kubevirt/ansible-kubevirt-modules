#!/usr/bin/env bash

set -xe

cluster-up/oc.sh adm policy add-scc-to-user privileged -n kubevirt -z kubevirt-operator
cluster-up/oc.sh adm policy add-scc-to-group anyuid system:authenticated

KUBEVIRT_VER=$(curl -s https://github.com/kubevirt/kubevirt/releases/latest | grep -o "v[0-9]\.[0-9]*\.[0-9]*")
CDI_VER=$(curl -s https://github.com/kubevirt/containerized-data-importer/releases/latest | grep -o "v[0-9]\.[0-9]*\.[0-9]*")
cluster-up/oc.sh apply -f https://github.com/kubevirt/containerized-data-importer/releases/download/$CDI_VER/cdi-operator.yaml
cluster-up/oc.sh apply -f https://github.com/kubevirt/containerized-data-importer/releases/download/$CDI_VER/cdi-operator-cr.yaml

cluster-up/oc.sh apply -f https://github.com/kubevirt/kubevirt/releases/download/$KUBEVIRT_VER/kubevirt-operator.yaml
cluster-up/oc.sh create configmap -n kubevirt kubevirt-config --from-literal feature-gates=DataVolumes
cluster-up/oc.sh apply -f https://github.com/kubevirt/kubevirt/releases/download/$KUBEVIRT_VER/kubevirt-cr.yaml


(
  cluster-up/oc.sh wait --timeout=240s --for=condition=Ready -n kubevirt kv/kubevirt ;
) || {
  echo "Something went wrong"
  cluster-up/oc.sh describe -n kubevirt kv/kubevirt
  cluster-up/oc.sh describe pods -n kubevirt
  exit 1
}

sleep 12

cluster-up/oc.sh describe nodes

