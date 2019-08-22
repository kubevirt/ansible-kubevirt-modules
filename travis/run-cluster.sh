#!/bin/bash

set -xe

# Look at https://github.com/fabiand/traviskube/tree/master/ci for inspiration on updating this script

BASE_DIR=$(dirname $(realpath $0))

bash -x $BASE_DIR/traviskube/start-cluster minikube

kubectl apply -f https://github.com/kubevirt/containerized-data-importer/releases/download/$CDI_VER/cdi-operator.yaml
if [[ $CDI_VER =~ ^v1\.[1-9]\. ]]; then
  kubectl apply -f https://github.com/kubevirt/containerized-data-importer/releases/download/$CDI_VER/cdi-operator-cr.yaml
else
  kubectl apply -f https://github.com/kubevirt/containerized-data-importer/releases/download/$CDI_VER/cdi-cr.yaml
fi

kubectl apply -f https://github.com/kubevirt/kubevirt/releases/download/$KUBEVIRT_VER/kubevirt-operator.yaml
kubectl create configmap -n kubevirt kubevirt-config --from-literal debug.useEmulation=true --from-literal feature-gates=DataVolumes
kubectl apply -f https://github.com/kubevirt/kubevirt/releases/download/$KUBEVIRT_VER/kubevirt-cr.yaml


(
  kubectl wait --timeout=240s --for condition=Available -n kubevirt kv/kubevirt ;
) || {
  echo "Something went wrong"
  kubectl describe -n kubevirt kv/kubevirt
  kubectl describe pods -n kubevirt
  exit 1
}

sleep 12

free -m
kubectl get pods --all-namespaces
kubectl describe nodes

