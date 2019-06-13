#!/bin/bash

set -xe

BASE_DIR=$(dirname $(realpath $0))
bash -x $BASE_DIR/traviskube/prepare-host minikube

