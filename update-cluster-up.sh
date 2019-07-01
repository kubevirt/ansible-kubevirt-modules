#!/bin/bash

# the kubevirtci commit hash to vendor from
kubevirtci_git_hash=c98f4dd10b382176cbe845671551ce1c0627ac07

# remove previous cluster-up dir entirely before vendoring
rm -rf cluster-up

# download and extract the cluster-up dir from a specific hash in kubevirtci
curl -L https://github.com/kubevirt/kubevirtci/archive/${kubevirtci_git_hash}/kubevirtci.tar.gz | tar xz kubevirtci-${kubevirtci_git_hash}/cluster-up --strip-component 1

