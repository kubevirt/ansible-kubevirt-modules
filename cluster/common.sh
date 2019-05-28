#!/bin/bash

CLUSTER_PROVIDER=${CLUSTER_PROVIDER:-k8s-1.13.3}
CLUSTER_NUM_NODES=${CLUSTER_NUM_NODES:-1}

provider_prefix=${JOB_NAME:-${CLUSTER_PROVIDER}}${EXECUTOR_NUMBER}
KUBE_CFG="$HOME/.kubeconfig-$provider_prefix"

kubectl() { cluster/kubectl "--kubeconfig=$KUBE_CFG" "$@"; }
gocli() { docker run --net=host --privileged --rm -v /var/run/docker.sock:/var/run/docker.sock kubevirtci/gocli:latest --prefix "$provider_prefix" "$@"; }

