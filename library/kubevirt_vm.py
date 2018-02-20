#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import base64
from kubernetes import client, config
import os
import time
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
        "name": {"required": False, "type": "str"},
        "namespace": {"required": False, "type": "str"},
        "wait": {"required": False, "type": "bool", "default": False},
        "timeout": {"required": False, "type": "int", "default": 20},
        "memory": {"required": False, "type": "str", "default": '64M'},
        "disk": {"required": False, "type": "str"},
        "lun": {"required": False, "type": "int", "default": 3},
        "iqn": {"required": False, "type": "str", "default": 'iqn.2017-01.io.kubevirt:sn.42'},
        "target": {"required": False, "type": "str", "default": 'iscsi-demo-target'},
        "src": {"required": False, "type": "str"},
        "cloudinit": {"required": False, "type": "str"},
        "cdrom": {"required": False, "type": "bool", "default": False},
    }
    module = AnsibleModule(argument_spec=argument_spec)
    config.load_kube_config()
    crds = client.CustomObjectsApi()
    name = module.params['name']
    namespace = module.params['namespace']
    wait = module.params['wait']
    timeout = module.params['timeout']
    memory = module.params['memory']
    disk = module.params['disk']
    target = module.params['target']
    iqn = module.params['iqn']
    lun = module.params['lun']
    cloudinit = module.params['cloudinit']
    cdrom = module.params['cdrom']
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
    if name is None:
        module.fail_json(msg='missing name')
    if namespace is None:
        module.fail_json(msg='missing namespace')
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
                if disk is not None:
                    registryvolume = {'volumeName': 'myvolume', 'registryDisk': {'image': disk}}
                else:
                    registryvolume = {'iscsi': {'targetPortal': target, 'iqn': iqn, 'lun': lun}, 'name': 'myvolume'}
                vm['spec']['volumes'].append(registryvolume)
                if cloudinit is not None:
                    if cdrom:
                        cloudinitdisk = {'volumeName': 'cloudinitvolume', 'cdrom': {'readOnly': True}, 'name': 'cloudinitdisk'}
                    else:
                        cloudinitdisk = {'volumeName': 'cloudinitvolume', 'disk': {'dev': 'vdb'}, 'name': 'cloudinitdisk'}
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
