#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from kubernetes import client, config
import os
import yaml

DOMAIN = "kubevirt.io"
VERSION = 'v1alpha1'


DOCUMENTATION = '''
module: kubevirt_vm
short_description: Handles kubevirt vms
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
- name: Create a vm
  kubevirt_vm:
    name: testvm
    namespace: default

- name: Delete that vm
  kubevirt_vm:
    name: testvm
    namespace: testvm
    state: absent
'''


def exists(crds, name, namespace):
    allvms = crds.list_cluster_custom_object(DOMAIN, VERSION, 'virtualmachines')["items"]
    vms = [vm for vm in allvms if vm.get("metadata")["namespace"] == namespace and vm.get("metadata")["name"] == name]
    result = True if vms else False
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
        "src": {"required": False, "type": "str"},
    }
    module = AnsibleModule(argument_spec=argument_spec)
    config.load_kube_config()
    crds = client.CustomObjectsApi()
    name = module.params['name']
    namespace = module.params['namespace']
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
                vm = {'kind': 'VirtualMachine', 'spec': {'terminationGracePeriodSeconds': 0, 'domain': {'resources': {'requests': {'memory': '64M'}}, 'devices': {'disks': [{'volumeName': 'myvolume', 'disk': {'dev': 'vda'}, 'name': 'mydisk'}]}}, 'volumes': [{'iscsi': {'targetPortal': 'iscsi-demo-target', 'iqn': 'iqn.2017-01.io.kubevirt:sn.42', 'lun': 3}, 'name': 'myvolume'}]}, 'apiVersion': 'kubevirt.io/v1alpha1', 'metadata': {'namespace': name, 'name': namespace}}
            meta = crds.create_namespaced_custom_object(DOMAIN, VERSION, namespace, 'virtualmachines', vm)

    else:
        if found:
            meta = crds.delete_namespaced_custom_object(DOMAIN, VERSION, namespace, 'virtualmachines', name, client.V1DeleteOptions())
            changed = True
            skipped = False
        else:
            changed = False
            skipped = True
            meta = {'result': 'skipped'}
    module.exit_json(changed=changed, skipped=skipped, meta=meta)

if __name__ == '__main__':
    main()
