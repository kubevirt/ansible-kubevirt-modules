#!/bin/bash

# TS
minishift logs -t 1

echo "$(minishift ip) minishift" | sudo tee -a /etc/hosts

## Prepare CDI
export CDI_VERSION=$(curl https://github.com/kubevirt/containerized-data-importer/releases/latest | grep -o "v[0-9]\.[0-9]*\.[0-9]*")
oc create -f https://github.com/kubevirt/containerized-data-importer/releases/download/$CDI_VERSION/cdi-operator.yaml
oc create -f https://github.com/kubevirt/containerized-data-importer/releases/download/$CDI_VERSION/cdi-operator-cr.yaml

get_remaining_pods() {
  oc get pods \
    --all-namespaces \
    --field-selector=status.phase!=Running,status.phase!=Succeeded ;
}

sleep 6;

while [[ "$( get_remaining_pods 2>&1 | wc -l)" -gt 2 ]];
do
  oc get pods --all-namespaces
  sleep 6;
done

# TS
minishift logs -t 1

## Execute test
ansible-playbook --version
ansible-playbook -vvv tests/playbooks/all.yml
RETVAL=$?

## Gather debug info
minishift status
minishift logs
minishift ssh 'ps auxw; docker ps -a; free -m; df -h'

for i in pvcs vmis vms pods; do
  oc get $i --all-namespaces
done

exit $RETVAL
