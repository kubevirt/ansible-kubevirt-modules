#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0
# (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

import copy
import re
import kubevirt as sdk

from kubevirt import V1DeleteOptions

HELPER_CLASS = {
    'virtual_machine': "VirtualMachineHelper"
}

COMMON_ARG_SPEC = {
    'state': {
        'default': 'present',
        'choices': ['present', 'absent'],
    },
    'force': {
        'type': 'bool',
        'default': False,
    },
    'resource_definition': {
        'type': 'dict',
        'aliases': ['definition', 'inline']
    },
    'src': {
        'type': 'path',
    },
    'kind': {},
    'name': {},
    'namespace': {},
    'api_version': {
        'default': 'v1',
        'aliases': ['api', 'version'],
    },
}

AUTH_ARG_SPEC = {
    'kubeconfig': {
        'type': 'path',
    },
    'context': {},
    'host': {},
    'api_key': {
        'no_log': True,
    },
    'username': {},
    'password': {
        'no_log': True,
    },
    'verify_ssl': {
        'type': 'bool',
    },
    'ssl_ca_cert': {
        'type': 'path',
    },
    'cert_file': {
        'type': 'path',
    },
    'key_file': {
        'type': 'path',
    },
}


def to_snake(name):
    """ Convert a tring from camel to snake """
    return re.sub(
        '((?<=[a-z0-9])[A-Z]|(?!^)(?<!_)[A-Z](?=[a-z]))', r'_\1', name).lower()


def get_helper(client, kind):
    """ Factory method for KubeVirt resources """
    if kind == 'virtual_machine':
        return VirtualMachineHelper(client)
    elif kind == 'offline_virtual_machine':
        return OfflineVirtualMachineHelper(client)
    elif kind == 'virtual_machine_replica_set':
        return VirtualMachineReplicaSetHelper(client)
    # FIXME: find/create a better exception (AnsibleModuleError?)
    raise Exception('Unknown kind %s' % kind)


class VirtualMachineHelper(object):
    """ Helper class for VirtualMachine resources """
    def __init__(self, client):
        self.__client = client

    def create(self, body, namespace):
        """ Create VirtualMachine resource """
        vm_body = sdk.V1VirtualMachine().to_dict()
        vm_body.update(copy.deepcopy(body))
        return self.__client.create_namespaced_virtual_machine(
            vm_body, namespace)

    def delete(self, name, namespace):
        """ Delete VirtualMachine resource """
        return self.__client.delete_namespaced_virtual_machine(
            V1DeleteOptions(), namespace, name)

    def exists(self, name, namespace):
        """ Return VirtualMachine resource, if exists """
        return self.__client.read_namespaced_virtual_machine(name, namespace)

    def replace(self, body, namespace, name):
        """ Replace VirtualMachine resource """
        vm_body = sdk.V1VirtualMachine().to_dict()
        vm_body.update(copy.deepcopy(body))
        return self.__client.replace_namespaced_virtual_machine(
            vm_body, namespace, name)


class OfflineVirtualMachineHelper(object):
    """ Helper class for OfflineVirtualMachine resources """
    def __init__(self, client):
        """ Class constructor """
        self.__client = client

    def create(self, body, namespace):
        """ Create OfflineVirtualMachine resource """
        ovm_body = sdk.V1OfflineVirtualMachine().to_dict()
        ovm_body.update(copy.deepcopy(body))
        return self.__client.create_namespaced_offline_virtual_machine(
            ovm_body, namespace)

    def delete(self, name, namespace):
        """ Delete OfflineVirtualMachine resource """
        return self.__client.delete_namespaced_offline_virtual_machine(
            V1DeleteOptions(), namespace, name)

    def exists(self, name, namespace):
        """ Return OfflineVirtualMachine resource, if exists """
        return self.__client.read_namespaced_offline_virtual_machine(
            name, namespace)


class VirtualMachineReplicaSetHelper(object):
    """ Helper class for VirtualMachineReplicaSet resources """
    def __init__(self, client):
        """ Class constructor """
        self.__client = client

    def create(self, body, namespace):
        """ Create VirtualMachine resource """
        ovm_body = sdk.V1VirtualMachineReplicaSet().to_dict()
        ovm_body.update(copy.deepcopy(body))
        return self.__client.create_namespaced_virtual_machine_replica_set(
            ovm_body, namespace)

    def delete(self, name, namespace):
        """ Delete VirtualMachine resource """
        return self.__client.delete_namespaced_virtual_machine_replica_set(
            V1DeleteOptions(), namespace, name)

    def exists(self, name, namespace):
        """ Return VirtualMachine resource, if exists """
        return self.__client.read_namespaced_virtual_machine_replica_set(
            name, namespace)
