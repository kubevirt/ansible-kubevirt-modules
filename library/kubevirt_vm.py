#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0 (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: kubevirt_vm
short_description: Manage KubeVirt VMs
description:
    - Create or delete a KubeVirt VM
version_added: "2.4.x"
author:
    - KubeVirt Team (@kubevirt)
options:
    state:
        description:
            - Whether to create (C(present)) or delete (C(absent)) the VM.
        required: false
        default: "present"
        choices: ["present", "absent"]
    name:
        description:
            - Name of the VM.
        required: true
    namespace:
        description:
            - Namespace to add the VM to or delete from.
        required: true
    wait:
        description:
            - Wait for the VM to start running.
        type: bool
        required: false
        default: 'no'
    timeout:
        description:
            - Maximum number of seconds to wait for.
        type: int
        required: false
        default: "20"
    memory:
        description:
            - Memory to assign to the VM.
        required: false
        default: "512M"
    pvc:
        description:
            - "Name of a PersistentVolumeClaim existing in the same namespace
              to use as a base disk for the VM."
        required: true
    src:
        description:
            - "Local YAML file to use as a source to define the VM.
               It overrides all parameters."
        required: false
    cloudinit:
        description:
            - "String containing cloudInit information to pass to the VM.
               It will be encoded as base64."
        required: false
    insecure:
        description:
            - "Disable SSL certificate verification."
        type: bool
        required: false
        default: "no"
notes:
    - Details at https://github.com/kubevirt/kubevirt
requirements:
    - Kubernetes Python package'''

EXAMPLES = '''
- name: Create a VM
  kubevirt_vm:
    name: testvm
    namespace: default

- name: Delete a VM
  kubevirt_vm:
    name: testvm
    namespace: default
    state: absent
'''

RETURN = ''' # '''

from ansible.module_utils.basic import AnsibleModule
from ansible import errors
from kubernetes import client, config
from kubernetes.client import Configuration
from kubernetes.client.rest import ApiException
import base64
import time
import yaml

DOMAIN = "kubevirt.io"
VERSION = 'v1alpha1'
REGISTRYDISKS = [
    'kubevirt/alpine-registry-disk-demo',
    'kubevirt/cirros-registry-disk-demo',
    'kubevirt/fedora-cloud-registry-disk-demo']


def build_vm_definition(params):
    '''return a dict() containing a VM definition based on params.'''

    vm_def = dict()
    spec = dict()
    domain = dict()
    resources = dict()
    devices = dict()
    devices["disks"] = list()
    disk = dict()
    metadata = dict()

    resources["requests"] = dict()
    resources["requests"]["memory"] = params.get("memory")

    disk["volumeName"] = "myvolume"
    disk["disk"] = dict({"dev": "vda"})
    disk["name"] = "mydisk"
    devices["disks"].append(disk)

    domain["resources"] = resources
    domain["devices"] = devices

    spec["terminationGracePeriodSeconds"] = 0
    spec["domain"] = domain
    spec["volumes"] = list()

    metadata["namespace"] = params.get("namespace")
    metadata["name"] = params.get("name")

    vm_def["kind"] = "VirtualMachine"
    vm_def["apiVersion"] = DOMAIN + "/" + VERSION
    vm_def["spec"] = spec
    vm_def["metadata"] = metadata

    return vm_def


def wait(crds, params):
    '''wait for the VM to be running.'''
    waittime = 0
    name = params.get("name")
    namespace = params.get("namespace")
    timeout = params.get("timeout")
    while True:
        currentstatus = status(crds, name, namespace)
        if currentstatus == 'Running':
            return True
        elif currentstatus == 'Not Found':
            return False
        elif waittime > timeout:
            return False
        else:
            waittime += 5
            time.sleep(5)


def build_volume_definition(pvc, registrydisk):
    '''build myvolume object with user provided data.'''
    myvolume = dict()
    myvolume["volumeName"] = "myvolume"
    myvolume["name"] = "myvolume"
    if registrydisk is not None:
        myvolume["registryDisk"] = dict({"image": registrydisk})
    elif pvc is not None:
        myvolume["persistentVolumeClaim"] = dict(
            {'claimName': pvc})
    return myvolume


def build_cloudinitdisk_definition():
    '''return cloudinitdisk dictionary.'''
    cloudinitdisk = dict()
    cloudinitdisk["volumeName"] = "cloudinitvolume"
    cloudinitdisk["cdrom"] = dict({"readOnly": True})
    cloudinitdisk["name"] = "cloudinitdisk"
    return cloudinitdisk


def build_cloudinitvol_definition(user_data):
    '''return cloudinitvolume dictionary.'''
    user_data_base64 = dict(
        {"userDataBase64": base64.b64encode(user_data)})
    cloudinitvolume = dict()
    cloudinitvolume["cloudInitNoCloud"] = user_data_base64
    cloudinitvolume["name"] = "cloudinitvolume"
    return cloudinitvolume


def validate_data(pvc, registrydisk):
    '''validate required that cannot be defined as required.'''
    if pvc is None and registrydisk is None:
        return False
    return True


def build_vm_from_src(src):
    '''build VM definition from source file.'''
    try:
        with open(src) as data:
            try:
                vm_def = yaml.load(data)
            except yaml.scanner.ScannerError as err:
                errors.AnsibleModuleError(str(err))
        if vm_def.get("metadata") is None:
            raise errors.AnsibleModuleError(
                "failed to get metadata from %s" % src)
    except IOError as err:
        raise errors.AnsibleModuleError(
            "Failed while opening %s: %s" % (src, str(err)))
    return vm_def


def create_vm(crds, vm_def):
    '''create vm and returns API answer.'''
    metadata = vm_def.get("metadata")
    try:
        meta = crds.create_namespaced_custom_object(
            DOMAIN, VERSION, metadata.get("namespace"),
            "virtualmachines", vm_def)
    except ApiException as err:
        raise errors.AnsibleModuleError("Error creating vm: %s" % err)
    return meta


def delete_vm(crds, name, namespace):
    '''delete vm and returns API answer.'''
    try:
        meta = crds.delete_namespaced_custom_object(
            DOMAIN, VERSION, namespace, 'virtualmachines', name,
            client.V1DeleteOptions())
    except ApiException as err:
        raise errors.AnsibleModuleError("Error deleting vm: %s" % str(err))
    return meta


def exists(crds, name, namespace):
    '''return true if the virtual machine already exists, otherwise false.'''
    all_vms = crds.list_cluster_custom_object(
        DOMAIN, VERSION, 'virtualmachines')["items"]
    vms = [
        vm for vm in all_vms if vm.get("metadata")["namespace"] == namespace
        and vm.get("metadata")["name"] == name]
    result = True if vms else False
    return result


def status(crds, name, namespace):
    '''return the current state of the offline virtual machine.'''
    try:
        vm_instance = crds.get_namespaced_custom_object(
            DOMAIN, VERSION, namespace, 'virtualmachines', name)
        return vm_instance['status']['phase']
    except ApiException as err:
        return err


def connect(params):
    '''return CustomObjectsApi object after parsing user options.'''
    config.load_kube_config()
    cfg = Configuration()
    if params.get("insecure"):
        cfg.verify_ssl = False
    api_client = client.ApiClient(configuration=cfg)
    return client.CustomObjectsApi(api_client=api_client)


def main():
    '''Entry point.'''
    argument_spec = {
        "state": {
            "default": "present",
            "choices": ['present', 'absent'],
            "type": 'str'
        },
        "name": {"required": True, "type": "str"},
        "namespace": {"required": True, "type": "str"},
        "wait": {"required": False, "type": "bool", "default": False},
        "timeout": {"required": False, "type": "int", "default": 20},
        "memory": {"required": False, "type": "str", "default": '512M'},
        "pvc": {"required": True, "type": "str"},
        "src": {"required": False, "type": "str"},
        "cloudinit": {"required": False, "type": "str"},
        "insecure": {"required": False, "type": "bool", "default": False}
    }
    module = AnsibleModule(argument_spec=argument_spec)
    crds = connect(module.params)
    registrydisk = None
    pvc = module.params['pvc']
    src = module.params['src']

    if not validate_data(pvc, registrydisk):
        module.fail_json(msg="Either pvc or registrydisk is required")

    if src is not None:
        vm_def = build_vm_from_src(src)
    else:
        vm_def = build_vm_definition(module.params)
        vm_def['spec']['volumes'].append(
            build_volume_definition(pvc, registrydisk))
        if module.params["cloudinit"] is not None:
            vm_def['spec']['domain']['devices']['disks'].append(
                build_cloudinitdisk_definition())
            vm_def['spec']['volumes'].append(
                build_cloudinitvol_definition(
                    module.params["cloudinit"]))

    found = exists(crds, module.params["name"], module.params["namespace"])

    if module.params["state"] == "present":
        if found:
            module.exit_json(
                changed=False, skipped=True, meta={"result": "skipped"})

        meta = create_vm(crds, vm_def)
        if module.params["wait"]:
            if not wait(crds, module.params):
                module.fail_json(
                    msg="Timed out waiting for the VM")
        module.exit_json(changed=True, skipped=False, meta=meta)

    else:
        if found:
            meta = delete_vm(
                crds, module.params["name"], module.params["namespace"])
            module.exit_json(changed=True, skipped=False, meta=meta)
        module.exit_json(
            changed=False, skipped=True, meta=dict({"result": "skipped"}))


if __name__ == '__main__':
    main()
