#!/bin/bash

set -x

kubectl get pods --all-namespaces

free -m
docker ps
docker ps -q|xargs docker stats --no-stream

kubectl get configmap -n kubevirt kubevirt-config -o yaml
kubectl get pvc -o yaml
kubectl get vmis -o yaml
kubectl get vms -o yaml

kubectl describe nodes

minikube logs
