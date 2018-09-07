#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0
# (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

import copy
import re
import kubernetes.client as core_sdk
import kubevirt as sdk

from kubernetes import watch
from kubevirt import V1DeleteOptions

NAME_ARG_SPEC = {
    'name': {
        'type': 'str',
        'required': False
    },
    'namespace': {
        'type': 'str',
        'required': False
    },
    'kind': {
        'type': 'str',
        'required': False
    },
    'api_version': {
        'type': 'str',
        'required': False,
        'default': 'v1',
        'aliases': ['api', 'version'],
    }
}

FACTS_ARG_SPEC = {
    'label_selectors': {
        'type': 'list',
        'default': []
    },
    'field_selectors': {
        'type': 'list',
        'default': []
    }
}

RESOURCE_ARG_SPEC = {
    'resource_definition': {
        'type': 'dict',
        'aliases': ['definition', 'inline']
    },
    'src': {
        'type': 'path',
    }
}

STATE_ARG_SPEC = {
    'state': {
        'default': 'present',
        'choices': ['present', 'absent'],
    },
    'force': {
        'type': 'bool',
        'default': False,
    },
    'wait': {
        'type': 'bool',
        'default': False,
    },
    'timeout': {
        'type': 'int',
        'default': 300,
    }
}

AUTH_ARG_SPEC = {
    'kubeconfig': {
        'type': 'path',
        'required': False
    },
    'context': {},
    'host': {
        'type': 'str',
        'required': False
    },
    'api_key': {
        'type': 'str',
        'no_log': True
    },
    'username': {
        'type': 'str',
        'required': False
    },
    'password': {
        'type': 'str',
        'no_log': True
    },
    'verify_ssl': {
        'type': 'bool',
        'required': False,
        'default': True
    },
    'ssl_ca_cert': {
        'type': 'path',
        'required': False
    },
    'cert_file': {
        'type': 'path',
        'required': False
    },
    'key_file': {
        'type': 'path',
        'required': False
    },
}


def to_snake(name):
    """ Convert a string from camel to snake """
    return re.sub(
        '((?<=[a-z0-9])[A-Z]|(?!^)(?<!_)[A-Z](?=[a-z]))', r'_\1', name).lower()


def get_helper(client, core_client, kind):
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
    elif kind == 'persistent_volume_claim':
        return PersistentVolumeClaimHelper(core_client)
    raise Exception('Unknown kind %s' % kind)


def _resource_version(current):
    if isinstance(current.metadata, dict):
        return current.metadata.get('resource_version')
    return current.metadata.resource_version


def _use_cdi(annotations, labels):
    IMPORT_ENDPOINT_KEY = 'cdi.kubevirt.io/storage.import.endpoint'
    endpoint = annotations.get(IMPORT_ENDPOINT_KEY)
    app_label = labels.get('app')
    return endpoint and app_label == 'containerized-data-importer'


class VirtualMachineInstanceHelper(object):
    """ Helper class for VirtualMachineInstance resources """
    def __init__(self, client):
        self.__client = client

    def create(self, body, namespace, wait=False, timeout=0):
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

    def list(self, namespace=None, name=None, field_selectors=None,
             label_selectors=None):
        """ Return a VirtualMachineInstancesList """
        result = None
        if name:
            result = self.exists(name, namespace)
        elif not namespace:
            result = self.list_all(field_selectors, label_selectors)
        else:
            result = self.__client.list_namespaced_virtual_machine_instance(
                namespace=namespace,
                field_selector=','.join(field_selectors),
                label_selector=','.join(label_selectors))
        return result

    def list_all(self, field_selectors=None, label_selectors=None):
        """ Return all VirtualMachineInstances in a list """
        return self.__client.list_virtual_machine_instance_for_all_namespaces(
            field_selector=','.join(field_selectors),
            label_selector=','.join(label_selectors)
        )

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

    def create(self, body, namespace, wait=False, timeout=0):
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

    def list(self, namespace=None, name=None, field_selectors=None,
             label_selectors=None):
        """ Return a VirtualMachineList """
        result = None
        if name:
            result = self.exists(name, namespace)
        elif not namespace:
            result = self.list_all(field_selectors, label_selectors)
        else:
            result = self.__client.list_namespaced_virtual_machine(
                namespace=namespace,
                field_selector=','.join(field_selectors),
                label_selector=','.join(label_selectors))
        return result

    def list_all(self, field_selectors=None, label_selectors=None):
        """ Return all VirtualMachines in a list """
        return self.__client.list_virtual_machine_for_all_namespaces(
            field_selector=','.join(field_selectors),
            label_selector=','.join(label_selectors)
        )

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

    def create(self, body, namespace, wait=False, timeout=0):
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

    def list(self, namespace=None, name=None, field_selectors=None,
             label_selectors=None):
        """ Return a VirtualMachineInstanceReplicaSetList """
        result = None
        if name:
            result = self.exists(name, namespace)
        elif not namespace:
            result = self.list_all(field_selectors, label_selectors)
        else:
            result = (self.__client.
                      list_namespaced_virtual_machine_instance_replica_set(
                          namespace=namespace,
                          field_selector=','.join(field_selectors),
                          label_selector=','.join(label_selectors)))
        return result

    def list_all(self, field_selectors=None, label_selectors=None):
        """ Return all VirtualMachineInstanceReplicaSets in a list """
        return (self.__client.
                list_virtual_machine_instance_replica_set_for_all_namespaces(
                    field_selector=','.join(field_selectors),
                    label_selector=','.join(label_selectors)))

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

    def create(self, body, namespace, wait=False, timeout=0):
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

    def list(self, namespace=None, name=None, field_selectors=None,
             label_selectors=None):
        """ Return a VirtualMachineInstancePresetList """
        result = None
        if name:
            result = self.exists(name, namespace)
        elif not namespace:
            result = self.list_all(field_selectors, label_selectors)
        else:
            result = (self.__client.
                      list_namespaced_virtual_machine_instance_preset(
                          namespace=namespace,
                          field_selector=','.join(field_selectors),
                          label_selector=','.join(label_selectors)))
        return result

    def list_all(self, field_selectors=None, label_selectors=None):
        """ Return all VirtualMachineInstancePresets in a list """
        return (self.__client.
                list_virtual_machine_instance_preset_for_all_namespaces(
                    field_selector=','.join(field_selectors),
                    label_selector=','.join(label_selectors)))

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


class PersistentVolumeClaimHelper(object):
    """ Helper class for PersistentVolumeClaim resources """

    def __init__(self, client):
        """ Class constructor """
        self.__client = client

    def create(self, body, namespace, wait=False, timeout=300):
        """ Create PersistentVolumeClaim resource """
        pvc_body = core_sdk.V1PersistentVolumeClaim().to_dict()
        pvc_body.update(copy.deepcopy(body))
        created_pvc = self.__client.create_namespaced_persistent_volume_claim(
            namespace=namespace, body=pvc_body)
        if not wait:
            return created_pvc

        w = watch.Watch()
        for event in w.stream(
            self.__client.list_namespaced_persistent_volume_claim,
                namespace=namespace,
                field_selector='metadata.name=' + pvc_body['metadata']['name'],
                timeout_seconds=timeout):
            entity = event['object']
            metadata = entity.metadata
            if entity.status.phase == 'Bound':
                annotations = metadata.annotations if \
                    metadata.annotations else {}
                IMPORT_STATUS_KEY = 'cdi.kubevirt.io/storage.import.pod.phase'
                import_status = annotations.get(IMPORT_STATUS_KEY)
                labels = metadata.labels if metadata.labels else {}
                if (not _use_cdi(annotations, labels) or
                        import_status == 'Succeeded'):
                    w.stop()
                    return entity
                elif entity.status.phase == 'Failed':
                    w.stop()
                    raise Exception("Failed to import PersistentVolumeClaim")
        raise Exception("Timeout exceed while waiting on result state of the \
                        entity.")

    def delete(self, name, namespace):
        """ Delete PersistentVolumeClaim resource """
        return self.__client.delete_namespaced_persistent_volume_claim(
            name=name, namespace=namespace, body={})

    def exists(self, name, namespace):
        """ Return PersistentVolumeClaim resource, if exists """
        return self.__client.read_namespaced_persistent_volume_claim(
            name, namespace, exact=True)

    def list(self, namespace=None, name=None, field_selectors=None,
             label_selectors=None):
        """ Return a PersistentVolumeClaim """
        result = None
        if name:
            result = self.exists(name, namespace)
        elif not namespace:
            result = self.list_all(field_selectors, label_selectors)
        else:
            result = self.__client.list_namespaced_persistent_volume_claim(
                namespace=namespace,
                field_selector=','.join(field_selectors),
                label_selector=','.join(label_selectors))
        return result

    def list_all(self, field_selectors=None, label_selectors=None):
        """ Return all PersistentVolumeClaim in a list """
        return self.__client.list_persistent_volume_claim_for_all_namespaces(
            field_selector=','.join(field_selectors),
            label_selector=','.join(label_selectors)
        )

    def replace(self, body, namespace, name):
        """ Replace PersistentVolumeClaim resource """
        current = self.exists(name, namespace)
        pvc_body = core_sdk.V1PersistentVolumeClaim(
            api_version=body.get('apiVersion'),
            kind=body.get('kind'),
            metadata=body.get('metadata'),
            spec=body.get('spec')
        )
        res_version = _resource_version(current)
        pvc_body.metadata['resourceVersion'] = res_version
        pvc_body.status = current.status
        return self.__client.replace_namespaced_persistent_volume_claim(
            pvc_body, namespace, name)
