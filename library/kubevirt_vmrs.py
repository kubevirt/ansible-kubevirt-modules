#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, Karim Boumedhel <@karmab>, Irina Gulina <@alexxa>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: kubevirt_vmrs
short_description: Manage KubeVirt VM ReplicaSets
description:
    - Create or delete a KubeVirt VM ReplicaSets
version_added: "2.4.x"
author:
    - Karim Boumedhel (@karmab)
    - Irina Gulina (@alexxa)
options:
    state:
        description:
            - Whether to create (C(present)) or delete (C(absent)) the VM ReplicaSet.
        required: false
        default: "present"
        choices: ["present", "absent"]
    name:
        description:
            - Name of the VM ReplicaSet.
        required: true
    namespace:
        description:
            - Namespace to add the VM ReplicaSet to or delete from.
        required: true
    replicas:
        description:
            - Number of desired pods.
        type: int
        required: false
        default: '3'
    memory:
        description:
            - Memory to assing to the VM ReplicaSet.
        required: false
        default: "64M"
    image:
        description:
            - Name of the image with the embedded disk.
        required: false
        default: 'kubevirt/cirros-registry-disk-demo:v0.2.0'
    label:
        description:
            - Attributes of the VM ReplicaSet.
        type: dict
        required: false
    src:
        description:
            - Local YAML file to use as a source to define the VM ReplicaSet. It overrides all parameters.
        required: false
notes:
    - Details at https://github.com/kubevirt/kubevirt
    - And https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/
requirements:
    - Kubernetes Python package'''

EXAMPLES = '''
- name: Create a VM ReplicaSet
  kubevirt_vmrs:
    name: testvm
    namespace: default
    labels:
      flavor: big

- name: Delete a VM ReplicaSet
  kubevirt_vmrs:
    name: testvm
    namespace: default
    state: absent
'''

RETURN = ''' # '''

from ansible.module_utils.basic import AnsibleModule
from kubernetes import client, config
import os
import yaml

DOMAIN = "kubevirt.io"
VERSION = 'v1alpha1'

def exists(crds, name, namespace):
    allvmrs = crds.list_cluster_custom_object(DOMAIN, VERSION, 'virtualmachinereplicasets')["items"]
    vmrss = [vmrs for vmrs in allvmrs if vmrs.get("metadata")["namespace"] == namespace and vmrs.get("metadata")["name"] == name]
    result = True if vmrss else False
    return result


def main():
    argument_spec = {
        "state": {
            "default": "present",
            "choices": ['present', 'absent'],
            "type": 'str'
        },
        "name": {"required": True, "type": "str"},
        "namespace": {"required": True, "type": "str"},
        "replicas": {"required": False, "type": "int", "default": 3},
        "memory": {"required": False, "type": "str", "default": '64M'},
        "image": {"required": False, "type": "str", "default": 'kubevirt/cirros-registry-disk-demo:v0.2.0'},
        "labels": {"required": False, "type": "dict"},
        "src": {"required": False, "type": "str"},
    }
    module = AnsibleModule(argument_spec=argument_spec)
    config.load_kube_config()
    crds = client.CustomObjectsApi()
    name = module.params['name']
    namespace = module.params['namespace']
    image = module.params['image']
    memory = module.params['memory']
    replicas = module.params['replicas']
    labels = module.params['labels']
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
                module.fail_json(msg="missing metadata")
            srcname = metadata.get("name")
            srcnamespace = metadata.get("namespace")
            if srcname is None or srcname != name:
                module.fail_json(msg='missing or different name in %s' % src)
            if srcnamespace is None or srcnamespace != namespace:
                module.fail_json(msg='missing or different namespace in %s' % src)
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
                vmrs = {'kind': 'VirtualMachineReplicaSet', 'spec': {'replicas': replicas, 'template': {'spec': {'domain': {'resources': {'requests': {'memory': memory}}, 'devices': {'disks': [{'volumeName': 'registryvolume', 'disk': {'dev': 'vda'}, 'name': 'registrydisk'}]}}, 'volumes': [{'name': 'registryvolume', 'registryDisk': {'image': image}}]}, 'metadata': {'name': name}}}, 'apiVersion': '%s/%s' % (DOMAIN, VERSION), 'metadata': {'name': name, 'namespace': namespace}}
                if labels is not None:
                    try:
                        vmrs['spec']['template']['metadata']['labels'] = labels
                        vmrs['spec']['selector'] = {'matchLabels': labels}
                    except yaml.scanner.ScannerError as err:
                        module.fail_json(msg="Couldn't parse labels, got %s" % err)
            try:
                meta = crds.create_namespaced_custom_object(DOMAIN, VERSION, namespace, 'virtualmachinereplicasets', vmrs)
            except Exception as err:
                module.fail_json(msg='Error creating virtualmachinereplicaset, got %s' % err)
    else:
        if found:
            try:
                meta = crds.delete_namespaced_custom_object(DOMAIN, VERSION, namespace, 'virtualmachinereplicasets', name, client.V1DeleteOptions())
            except Exception as err:
                module.fail_json(msg='Error deleting virtualmachinereplicaset, got %s' % err)
            changed = True
            skipped = False
        else:
            changed = False
            skipped = True
            meta = {'result': 'skipped'}
    module.exit_json(changed=changed, skipped=skipped, meta=meta)

if __name__ == '__main__':
    main()
