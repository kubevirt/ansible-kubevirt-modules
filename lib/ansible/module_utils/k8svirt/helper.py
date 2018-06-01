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

FACTS_ARG_SPEC = dict(
    name=dict(type='str', required=True),
    namespace=dict(type='str', required=True)
)

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


def _resource_version(current):
    if isinstance(current.metadata, dict):
        return current.metadata.get('resource_version')
    return current.metadata.resource_version


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
        return self.__client.read_namespaced_virtual_machine(
            name, namespace, exact=True)

    def replace(self, body, namespace, name):
        """ Replace VirtualMachine resource """
        current = self.exists(name, namespace)
        vm_body = sdk.V1VirtualMachine(
            api_version=body.get('apiVersion'),
            kind=body.get('kind'),
            metadata=body.get('metadata'),
            spec=body.get('spec')
        )
        res_version = _resource_version(current)
        vm_body.metadata['resourceVersion'] = res_version
        vm_body.status = current.status
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
            name, namespace, exact=True)

    def replace(self, body, namespace, name):
        """ Replace OfflineVirtualMachine resource """
        current = self.exists(name, namespace)
        ovm_body = sdk.V1OfflineVirtualMachine(
            api_version=body.get('apiVersion'),
            kind=body.get('kind'),
            metadata=body.get('metadata'),
            spec=body.get('spec')
        )
        res_version = _resource_version(current)
        ovm_body.metadata['resourceVersion'] = res_version
        ovm_body.status = current.status
        return self.__client.replace_namespaced_offline_virtual_machine(
            ovm_body, namespace, name)


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
            name, namespace, exact=True)

    def replace(self, body, namespace, name):
        """ Replace Virtual Machine ReplicaSet """
        current = self.exists(name, namespace)
        vmrs_body = sdk.V1VirtualMachineReplicaSet(
            api_version=body.get('apiVersion'),
            kind=body.get('kind'),
            metadata=body.get('metadata'),
            spec=body.get('spec')
        )
        res_version = _resource_version(current)
        vmrs_body.metadata['resourceVersion'] = res_version
        vmrs_body.status = current.status
        import q; q.q(name)
        return self.__client.replace_namespaced_virtual_machine_replica_set(
            vmrs_body, namespace, name)
