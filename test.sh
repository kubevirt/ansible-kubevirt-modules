#!/bin/bash

echo "$(minikube ip) minikube" | sudo tee -a /etc/hosts

## Prepare CDI
export VERSION=$(curl -s https://github.com/kubevirt/containerized-data-importer/releases/latest | grep -o "v[0-9]\.[0-9]*\.[0-9]*")
kubectl create -f https://github.com/kubevirt/containerized-data-importer/releases/download/$VERSION/cdi-operator.yaml
kubectl create -f https://github.com/kubevirt/containerized-data-importer/releases/download/$VERSION/cdi-operator-cr.yaml

## No HW virt
kubectl create configmap -n kubevirt kubevirt-config --from-literal debug.useEmulation=true --from-literal feature-gates=DataVolumes
kubectl scale --replicas=0 deployment/virt-controller -n kubevirt
kubectl scale --replicas=2 deployment/virt-controller -n kubevirt
kubectl scale --replicas=0 deployment/virt-api -n kubevirt
kubectl scale --replicas=2 deployment/virt-api -n kubevirt

get_remaining_pods() {
  kubectl get pods \
    --all-namespaces \
    --field-selector=status.phase!=Running,status.phase!=Succeeded ;
}

sleep 6;

while [[ "$( get_remaining_pods 2>&1 | wc -l)" -gt 2 ]];
do
  kubectl get pods --all-namespaces
  sleep 6;
done

## Execute test
ansible-playbook --version
ansible-playbook -vvv tests/roles/deploy.yml
ansible-playbook -vvv tests/playbooks/all.yml
