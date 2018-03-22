#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, Karim Boumedhel <@karmab>, Irina Gulina <@alexxa>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import AnsibleModule
import base64
from kubernetes import client, config
import os
import time
import yaml

DOMAIN = "kubevirt.io"
VERSION = 'v1alpha1'


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
    - Karim Boumedhel (@karmab)
    - Irina Gulina (@alexxa)
options:
    state:
        description:
            - Whether to create (C(present)) or delete (C(absent)) a VM.
        required: false
        default: "present"
        choices: ["present", "absent"]
    name:
        description:
            - Name of a VM.
        required: true
    namespace:
        description:
            - Namespace to add a VM to or delete from.
        required: true
    wait:
        description:
            - Wait for a VM to be running.
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
        description
            -
        required: false
        default: "512M"
    disk:
        description:
            - Attach a volume as a disk to a VM.
        required: false
    pvc:
        description:
            - Name of a PersistentVolumeClaim existing in the same namespace to use as a base disk for a VM.
        required: false
    src:
        description:
            - Local YAML file to use as a source to define a VM. It overrides all parameters.
        required: false
    cloudinit:
        description:
            - String containing cloudInit information to pass to a VM. It will be encoded as base64.
        required: false
    cdrom:
        description:
            - Attach a volume as a CD-ROM to a VM.
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

- name: Delete A VM
  kubevirt_vm:
    name: testvm
    namespace: testvm
    state: absent
'''

REGISTRYDISKS = ['kubevirt/alpine-registry-disk-demo', 'kubevirt/cirros-registry-disk-demo', 'kubevirt/fedora-cloud-registry-disk-demo']


def exists(crds, name, namespace):
    allvms = crds.list_cluster_custom_object(DOMAIN, VERSION, 'virtualmachines')["items"]
    vms = [vm for vm in allvms if vm.get("metadata")["namespace"] == namespace and vm.get("metadata")["name"] == name]
    result = True if vms else False
    return result


def status(crds, name, namespace):
    try:
        vm = crds.get_namespaced_custom_object(DOMAIN, VERSION, namespace, 'virtualmachines', name)
        return vm['status']['phase']
    except Exception as err:
        return err


def main():
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
        "registrydisk": {"required": False, "type": "str", "choices": REGISTRYDISKS},
        "pvc": {"required": False, "type": "str"},
        "src": {"required": False, "type": "str"},
        "cloudinit": {"required": False, "type": "str"},
    }
    module = AnsibleModule(argument_spec=argument_spec)
    config.load_kube_config()
    crds = client.CustomObjectsApi()
    name = module.params['name']
    namespace = module.params['namespace']
    wait = module.params['wait']
    timeout = module.params['timeout']
    memory = module.params['memory']
    registrydisk = module.params['registrydisk']
    pvc = module.params['pvc']
    cloudinit = module.params['cloudinit']
    src = module.params['src']
    state = module.params['state']
    if src is not None:
        if not os.path.exists(src):
            module.fail_json(msg='src %s not found' % src)
        else:
            with open(src) as data:
                try:
                    vm = yaml.load(data)
                except yaml.scanner.ScannerError as err:
                    module.fail_json(msg='Error parsing src file, got %s' % err)
            metadata = vm.get("metadata")
            if metadata is None:
                module.fail_json(msg='missing metadata')
            srcname = metadata.get("name")
            srcnamespace = metadata.get("namespace")
            if srcname is None or srcname != name:
                module.fail_json(msg='Different name found in src file')
            if srcnamespace is not None and srcnamespace != namespace:
                module.fail_json(msg='Different namespace found in src file')
    found = exists(crds, name, namespace)
    if state == 'present':
        if found:
            changed = False
            skipped = True
            meta = {'result': 'skipped'}
        else:
            changed = True
            skipped = False
            if src is None:
                vm = {'kind': 'VirtualMachine', 'spec': {'terminationGracePeriodSeconds': 0, 'domain': {'resources': {'requests': {'memory': memory}}, 'devices': {'disks': [{'volumeName': 'myvolume', 'disk': {'dev': 'vda'}, 'name': 'mydisk'}]}}, 'volumes': []}, 'apiVersion': 'kubevirt.io/v1alpha1', 'metadata': {'namespace': namespace, 'name': name}}
                if registrydisk is not None:
                    myvolume = {'volumeName': 'myvolume', 'registryDisk': {'image': registrydisk}, 'name': 'myvolume'}
                elif pvc is not None:
                    myvolume = {'volumeName': 'myvolume', 'persistentVolumeClaim': {'claimName': pvc}, 'name': 'myvolume'}
                else:
                    module.fail_json(msg='Missing disk information')
                vm['spec']['volumes'].append(myvolume)
                if cloudinit is not None:
                    cloudinitdisk = {'volumeName': 'cloudinitvolume', 'cdrom': {'readOnly': True}, 'name': 'cloudinitdisk'}
                    vm['spec']['domain']['devices']['disks'].append(cloudinitdisk)
                    userDataBase64 = base64.b64encode(cloudinit)
                    cloudinitvolume = {'cloudInitNoCloud': {'userDataBase64': userDataBase64}, 'name': 'cloudinitvolume'}
                    vm['spec']['volumes'].append(cloudinitvolume)
            try:
                meta = crds.create_namespaced_custom_object(DOMAIN, VERSION, namespace, 'virtualmachines', vm)
            except Exception as err:
                    module.fail_json(msg='Error creating vm, got %s' % err)
            if wait:
                waittime = 0
                while True:
                    currentstatus = status(crds, name, namespace)
                    if currentstatus == 'Running':
                        break
                    elif currentstatus == 'Not Found':
                        module.fail_json(msg='Vm not found')
                    elif waittime > timeout:
                        module.fail_json(msg='timeout waiting for vm to be running')
                    else:
                        waittime += 5
                        time.sleep(5)
    else:
        if found:
            try:
                meta = crds.delete_namespaced_custom_object(DOMAIN, VERSION, namespace, 'virtualmachines', name, client.V1DeleteOptions())
            except Exception as err:
                    module.fail_json(msg='Error deleting vm, got %s' % err)
            changed = True
            skipped = False
        else:
            changed = False
            skipped = True
            meta = {'result': 'skipped'}
    module.exit_json(changed=changed, skipped=skipped, meta=meta)


if __name__ == '__main__':
    main()
