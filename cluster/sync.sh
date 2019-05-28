#!/usr/bin/env bash

set -xe

source cluster/common.sh

KUBEVIRT_VER=$(curl -s https://github.com/kubevirt/kubevirt/releases/latest | grep -o "v[0-9]\.[0-9]*\.[0-9]*")
CDI_VER=$(curl -s https://github.com/kubevirt/containerized-data-importer/releases/latest | grep -o "v[0-9]\.[0-9]*\.[0-9]*")
kubectl apply -f https://github.com/kubevirt/kubevirt/releases/download/$KUBEVIRT_VER/kubevirt-operator.yaml
kubectl create configmap -n kubevirt kubevirt-config --from-literal feature-gates=DataVolumes
kubectl apply -f https://github.com/kubevirt/kubevirt/releases/download/$KUBEVIRT_VER/kubevirt-cr.yaml

kubectl apply -f https://github.com/kubevirt/containerized-data-importer/releases/download/$CDI_VER/cdi-operator.yaml
kubectl apply -f https://github.com/kubevirt/containerized-data-importer/releases/download/$CDI_VER/cdi-operator-cr.yaml

kubectl get ns
