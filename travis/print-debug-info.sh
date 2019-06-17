#!/bin/bash

kubectl get configmap -n kubevirt kubevirt-config -o yaml
kubectl get pvc -o yaml
kubectl get vmis -o yaml
kubectl get vms -o yaml
kubectl get pods --all-namespaces

