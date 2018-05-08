#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0
# (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

import re
from ansible import errors

DOMAIN = "kubevirt.io"
VERSION = "v1alpha1"

ARG_SPEC_COMMON = {
    "state": {
        "default": "present",
        "choices": ['present', 'absent'],
        "type": 'str'
    },
    "name": {"required": True, "type": "str"},
    "namespace": {"required": True, "type": "str"},
    "cores": {"required": False, "type": "int", "default": 2},
    "memory": {"required": False, "type": "str", "default": '512M'},
    "pvc": {"required": False, "type": "str"},
    "src": {"required": False, "type": "str"},
    "cloudinit": {"required": False, "type": "str"},
    "insecure": {"required": False, "type": "bool", "default": False},
    "labels": {"required": False, "type": "dict"}
}

ARG_SPEC_OVM = {
    "state": {
        "default": "present",
        "choices": ["present", "running", "absent"],
        "type": "str"
    }
}

ARG_SPEC_VMRS = {
    "state": {
        "default": "present",
        "choices": ["present", "paused", "absent"],
        "type": "str"
    },
    "selector": {"required": True, "type": "dict"},
    "replicas": {"required": False, "type": "int", "default": 1}
}

KIND_TRANS = {
    "virtualmachines": "VirtualMachine",
    "offlinevirtualmachines": "OfflineVirtualMachine",
    "virtualmachinereplicasets": "VirtualMachineReplicaSet"
}


def to_snake(name):
    """ Convert a tring from camel to snake """
    return re.sub(
        '((?<=[a-z0-9])[A-Z]|(?!^)(?<!_)[A-Z](?=[a-z]))', r'_\1', name).lower()


def get_spec(api_group):
    '''return argument_spec based on api_group.'''
    arg_spec = dict()
    arg_spec.update(ARG_SPEC_COMMON)
    if api_group == "virtualmachines":
        return arg_spec

    if api_group == "offlinevirtualmachines":
        arg_spec.update(ARG_SPEC_OVM)
        return arg_spec

    if api_group == "virtualmachinereplicasets":
        arg_spec.update(ARG_SPEC_VMRS)
        return arg_spec

    raise errors.AnsibleModuleError("unknown API group %s" % api_group)


def validate_data(pvc, registrydisk):
    '''validate required that cannot be defined as required.'''
    if pvc is None and registrydisk is None:
        return False
    return True
