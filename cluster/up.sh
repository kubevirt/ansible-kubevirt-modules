#!/usr/bin/env bash

set -xe

source cluster/common.sh

if [ $CLUSTER_TYPE == openshift ]; then
  # Openshift needs some more args
  GOCLI_RUN_EXTRA_ARGS="${GOCLI_RUN_EXTRA_ARGS} --ocp-port 8443 --reverse"
fi

if [ ! -x cluster/kubectl ]; then
  KUBECTL_VER=v1.14.2
  curl -L https://storage.googleapis.com/kubernetes-release/release/${KUBECTL_VER}/bin/linux/amd64/kubectl -o cluster/kubectl
  chmod a+rx cluster/kubectl
fi

gocli run --random-ports --nodes "$CLUSTER_NUM_NODES" --background $GOCLI_RUN_EXTRA_ARGS "kubevirtci/$CLUSTER_PROVIDER"

if [ $CLUSTER_TYPE == openshift ]; then
  gocli scp /etc/origin/master/admin.kubeconfig - > $KUBE_CFG
  cp $KUBE_CFG ${KUBE_CFG}.orig
  gocli scp /usr/bin/oc - > cluster/oc
  chmod a+rx cluster/oc
  # Old enough kubectl will just silently do nothing on 'config set-cluster'
  # (Some versions of?) `oc` do that as well, so use latest kubectl here
  kubectl config set-cluster node01:8443 --server=https://127.0.0.1:8443
  kubectl config set-cluster node01:8443 --insecure-skip-tls-verify=true
  oc whoami
else
  gocli scp /etc/kubernetes/admin.conf - > $KUBE_CFG
  cp $KUBE_CFG ${KUBE_CFG}.orig
  kubectl config set-cluster kubernetes --server=https://127.0.0.1:$(gocli ports k8s|tr -d '\r\n')
  kubectl config set-cluster kubernetes --insecure-skip-tls-verify=true
fi
# A bit of debugging info
diff -urN ${KUBE_CFG}.orig $KUBE_CFG || :

_kubectl get nodes
