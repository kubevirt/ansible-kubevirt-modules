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
    """ Convert a string from camel to snake """
    return re.sub(
        '((?<=[a-z0-9])[A-Z]|(?!^)(?<!_)[A-Z](?=[a-z]))', r'_\1', name).lower()


def get_helper(client, kind):
    """ Factory method for KubeVirt resources """
    if kind == 'virtual_machine_instance':
        return VirtualMachineInstanceHelper(client)
    elif kind == 'virtual_machine':
        return VirtualMachineHelper(client)
    elif kind == 'virtual_machine_instance_replica_set':
        return VirtualMachineInstanceReplicaSetHelper(client)
    elif kind == 'virtual_machine_instance_preset':
        return VirtualMachineInstancePreSetHelper(client)
    # FIXME: find/create a better exception (AnsibleModuleError?)
    raise Exception('Unknown kind %s' % kind)


def _resource_version(current):
    if isinstance(current.metadata, dict):
        return current.metadata.get('resource_version')
    return current.metadata.resource_version


class VirtualMachineInstanceHelper(object):
    """ Helper class for VirtualMachineInstance resources """
    def __init__(self, client):
        self.__client = client

    def create(self, body, namespace):
        """ Create VirtualMachineInstance resource """
        vmi_body = sdk.V1VirtualMachineInstance().to_dict()
        vmi_body.update(copy.deepcopy(body))
        return self.__client.create_namespaced_virtual_machine_instance(
            vmi_body, namespace)

    def delete(self, name, namespace):
        """ Delete VirtualMachineInstance resource """
        return self.__client.delete_namespaced_virtual_machine_instance(
            V1DeleteOptions(), namespace, name)

    def exists(self, name, namespace):
        """ Return VirtualMachineInstance resource, if exists """
        return self.__client.read_namespaced_virtual_machine_instance(
            name, namespace, exact=True)

    def replace(self, body, namespace, name):
        """ Replace VirtualMachineInstance resource """
        current = self.exists(name, namespace)
        vmi_body = sdk.V1VirtualMachineInstance(
            api_version=body.get('apiVersion'),
            kind=body.get('kind'),
            metadata=body.get('metadata'),
            spec=body.get('spec')
        )
        res_version = _resource_version(current)
        vmi_body.metadata['resourceVersion'] = res_version
        vmi_body.status = current.status
        return self.__client.replace_namespaced_virtual_machine_instance(
            vmi_body, namespace, name)


class VirtualMachineHelper(object):
    """ Helper class for VirtualMachine resources """
    def __init__(self, client):
        """ Class constructor """
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


class VirtualMachineInstanceReplicaSetHelper(object):
    """ Helper class for VirtualMachineInstanceReplicaSet resources """
    def __init__(self, client):
        """ Class constructor """
        self.__client = client

    def create(self, body, namespace):
        """ Create VirtualMachineInstanceReplicaSet resource """
        vmirs_body = sdk.V1VirtualMachineInstanceReplicaSet().to_dict()
        vmirs_body.update(copy.deepcopy(body))
        return (self.__client.
                create_namespaced_virtual_machine_instance_replica_set(
                    vmirs_body, namespace))

    def delete(self, name, namespace):
        """ Delete VirtualMachineInstanceReplicaSet resource """
        return (self.__client.
                delete_namespaced_virtual_machine_instance_replica_set(
                    V1DeleteOptions(), namespace, name))

    def exists(self, name, namespace):
        """ Return VirtualMachineInstanceReplicaSet resource, if exists """
        return (self.__client.
                read_namespaced_virtual_machine_instance_replica_set(
                    name, namespace, exact=True))

    def replace(self, body, namespace, name):
        """ Replace VirtualMachineInstanceReplicaSet """
        current = self.exists(name, namespace)
        vmirs_body = sdk.V1VirtualMachineInstanceReplicaSet(
            api_version=body.get('apiVersion'),
            kind=body.get('kind'),
            metadata=body.get('metadata'),
            spec=body.get('spec')
        )
        res_version = _resource_version(current)
        vmirs_body.metadata['resourceVersion'] = res_version
        vmirs_body.status = current.status
        return (self.__client.
                replace_namespaced_virtual_machine_instance_replica_set(
                    vmirs_body, namespace, name))


class VirtualMachineInstancePreSetHelper(object):
    """ Helper class for VirtualMachineInstancePreSet resources """
    def __init__(self, client):
        """ Class constructor """
        self.__client = client

    def create(self, body, namespace):
        """ Create VirtualMachineInstancePreset resource """
        vmps_body = sdk.V1VirtualMachineInstancePreset().to_dict()
        vmps_body.update(copy.deepcopy(body))
        return self.__client.create_namespaced_virtual_machine_instance_preset(
            vmps_body, namespace)

    def delete(self, name, namespace):
        """ Delete VirtualMachineInstancePreset resource """
        return self.__client.delete_namespaced_virtual_machine_instance_preset(
            V1DeleteOptions(), namespace, name)

    def exists(self, name, namespace):
        """ Return VirtualMachineInstancePreset resource, if exists """
        return self.__client.read_namespaced_virtual_machine_instance_preset(
            name, namespace, exact=True)

    def replace(self, body, namespace, name):
        """ Replace VirtualMachineInstancePreSet """
        current = self.exists(name, namespace)
        vmips_body = sdk.V1VirtualMachineInstancePreset(
            api_version=body.get('apiVersion'),
            kind=body.get('kind'),
            metadata=body.get('metadata'),
            spec=body.get('spec')
        )
        res_version = _resource_version(current)
        vmips_body.metadata['resourceVersion'] = res_version
        return (self.__client.
                replace_namespaced_virtual_machine_instance_preset(
                    vmips_body, namespace, name))
