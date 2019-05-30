#!/bin/bash

CLUSTER_PROVIDER=${CLUSTER_PROVIDER:-k8s-1.13.3}
CLUSTER_NUM_NODES=${CLUSTER_NUM_NODES:-2}

provider_prefix=${JOB_NAME:-${CLUSTER_PROVIDER}}${EXECUTOR_NUMBER}
KUBE_CFG="$HOME/.kubeconfig-$provider_prefix"

if [[ $CLUSTER_PROVIDER == os-* ]]; then
  CLUSTER_TYPE=openshift
  _kubectl() { oc "$@"; }
elif [[ $CLUSTER_PROVIDER == k8s-* ]]; then
  CLUSTER_TYPE=kubernetes
  _kubectl() { kubectl "$@"; }
fi

oc() { cluster/oc "--kubeconfig=$KUBE_CFG" "$@"; }
kubectl() { cluster/kubectl "--kubeconfig=$KUBE_CFG" "$@"; }
gocli() { docker run --net=host --privileged --rm -v /var/run/docker.sock:/var/run/docker.sock kubevirtci/gocli:latest --prefix "$provider_prefix" "$@"; }

