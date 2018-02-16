#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from kubernetes import client, config
import os
import yaml

DOMAIN = "kubevirt.io"
VERSION = 'v1alpha1'


DOCUMENTATION = '''
module: kubevirt_vmrs
short_description: Handles kubevirt vm replicasets
description:
    - Longer description of the module
    - Use name, namespace and src
version_added: "0.1"
author: "Karim Boumedhel, @karmab"
notes:
    - Details at https://github.com/kubevirt/kubevirt
requirements:
    - kubernetes python package you can grab from pypi'''

EXAMPLES = '''
- name: Create a virtualmachinereplicaset
  kubevirt_vmrs:
    name: testvm
    namespace: default

- name: Delete a virtualmachinereplicaset
  kubevirt_vmrs:
    name: testvm
    namespace: testvm
    state: absent
'''


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
        "name": {"required": False, "type": "str"},
        "namespace": {"required": False, "type": "str"},
        "replicas": {"required": False, "type": "int", "default": 3},
        "memory": {"required": False, "type": "str", "default": '64M'},
        "image": {"required": False, "type": "str", "default": 'kubevirt/cirros-registry-disk-demo:v0.2.0'},
        "labels": {"required": False, "type": "int"},
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
            name = vm.get("metadata")["name"]
            namespace = vm.get("metadata")["namespace"]
    if name is None and namespace is None:
        module.fail_json(msg='missing name/namespace')
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
                vmrs = {'kind': 'VirtualMachineReplicaSet', 'spec': {'replicas': replicas, 'template': {'spec': {'domain': {'resources': {'requests': {'memory': memory}}, 'devices': {'disks': [{'volumeName': 'registryvolume', 'disk': {'dev': 'vda'}, 'name': 'registrydisk'}]}}, 'volumes': [{'name': 'registryvolume', 'registryDisk': {'image': image}}]}, 'metadata': {'name': name}}}, 'apiVersion': 'kubevirt.io/v1alpha1', 'metadata': {'name': name, 'namespace': namespace}}
                if labels is not None:
                    try:
                        labels = yaml.load(labels)
                        vmrs['spec']['template']['metadata']['labels'] = labels
                        vmrs['spec']['selector'] = {'matchLabels': labels}
                    except yaml.scanner.ScannerError as err:
                        module.fail_json(msg="Couldn't parse labels, got %s" % err)
            meta = crds.create_namespaced_custom_object(DOMAIN, VERSION, namespace, 'virtualmachinereplicasets', vmrs)

    else:
        if found:
            meta = crds.delete_namespaced_custom_object(DOMAIN, VERSION, namespace, 'virtualmachinereplicasets', name, client.V1DeleteOptions())
            changed = True
            skipped = False
        else:
            changed = False
            skipped = True
            meta = {'result': 'skipped'}
    module.exit_json(changed=changed, skipped=skipped, meta=meta)

if __name__ == '__main__':
    main()
