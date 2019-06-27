#!/bin/bash

# the kubevirtci commit hash to vendor from
kubevirtci_git_hash=fec1b777f912ff0b7195cc76b452885e429a2203

# remove previous cluster-up dir entirely before vendoring
rm -rf cluster-up

# download and extract the cluster-up dir from a specific hash in kubevirtci
curl -L https://github.com/kubevirt/kubevirtci/archive/${kubevirtci_git_hash}/kubevirtci.tar.gz | tar xz kubevirtci-${kubevirtci_git_hash}/cluster-up --strip-component 1

