#!/usr/bin/env bash

set -xe

source cluster/common.sh

if [[ $CLUSTER_PROVIDER == os-* ]]; then
  # Openshift needs some more args
  GOCLI_RUN_EXTRA_ARGS="${GOCLI_RUN_EXTRA_ARGS} --ocp-port 8443 --reverse"
fi

if [ ! -x cluster/kubectl ]; then
  curl -L https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl -o cluster/kubectl
  chmod a+rx cluster/kubectl
fi

gocli run --random-ports --nodes "$CLUSTER_NUM_NODES" --background $GOCLI_RUN_EXTRA_ARGS "kubevirtci/$CLUSTER_PROVIDER"

gocli scp /etc/kubernetes/admin.conf - > $KUBE_CFG
kubectl config set-cluster kubernetes --server=https://127.0.0.1:$(gocli ports k8s|tr -d '\r\n')
kubectl config set-cluster kubernetes --insecure-skip-tls-verify=true

kubectl get pods -n kube-system

