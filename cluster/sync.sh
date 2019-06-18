#!/usr/bin/env bash

set -xe

source cluster/common.sh

if [[ $CLUSTER_TYPE == openshift ]]; then
  oc adm policy add-scc-to-user privileged -n kubevirt -z kubevirt-operator
  oc adm policy add-scc-to-group anyuid system:authenticated
fi

KUBEVIRT_VER=$(curl -s https://github.com/kubevirt/kubevirt/releases/latest | grep -o "v[0-9]\.[0-9]*\.[0-9]*")
CDI_VER=$(curl -s https://github.com/kubevirt/containerized-data-importer/releases/latest | grep -o "v[0-9]\.[0-9]*\.[0-9]*")
_kubectl apply -f https://github.com/kubevirt/kubevirt/releases/download/$KUBEVIRT_VER/kubevirt-operator.yaml
_kubectl create configmap -n kubevirt kubevirt-config --from-literal feature-gates=DataVolumes
_kubectl apply -f https://github.com/kubevirt/kubevirt/releases/download/$KUBEVIRT_VER/kubevirt-cr.yaml

_kubectl apply -f https://github.com/kubevirt/containerized-data-importer/releases/download/$CDI_VER/cdi-operator.yaml
_kubectl apply -f https://github.com/kubevirt/containerized-data-importer/releases/download/$CDI_VER/cdi-operator-cr.yaml

_kubectl get ns
