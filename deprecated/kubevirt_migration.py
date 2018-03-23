#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from kubernetes import client, config
import os
import yaml

DOMAIN = "kubevirt.io"
VERSION = 'v1alpha1'


DOCUMENTATION = '''
module: kubevirt_migration
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
- name: Migrate a migration
  kubevirt_migration:
    name: testvm
    namespace: default

- name: Remove that migration
  kubevirt_migration:
    name: testvm
    namespace: testvm
    state: absent
'''


def exists(crds, name, namespace):
    allmigrations = crds.list_cluster_custom_object(DOMAIN, VERSION, 'migrations')["items"]
    migrations = [migration for migration in allmigrations if migration.get("metadata")["namespace"] == namespace and migration.get("metadata")["name"] == name]
    result = True if migrations else False
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
        "host": {"required": False, "type": "str"},
        "src": {"required": False, "type": "str"},
    }
    module = AnsibleModule(argument_spec=argument_spec)
    config.load_kube_config()
    crds = client.CustomObjectsApi()
    name = module.params['name']
    namespace = module.params['namespace']
    host = module.params['host']
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
                migration = {'kind': 'Migration', 'spec': {'selector': {'name': name}}, 'apiVersion': '%s/%s' % (DOMAIN, VERSION), 'metadata': {'name': name, 'namespace': namespace}}
                if host is not None:
                    migration['spec']['nodeSelector'] == {'kubernetes.io/hostname': host}
            try:
                meta = crds.create_namespaced_custom_object(DOMAIN, VERSION, namespace, 'migrations', migration)
            except Exception as err:
                module.fail_json(msg='Error creating migration, got %s' % err)
    else:
        if found:
            try:
                meta = crds.delete_namespaced_custom_object(DOMAIN, VERSION, namespace, 'migrations', name, client.V1DeleteOptions())
            except Exception as err:
                module.fail_json(msg='Error deleting migration, got %s' % err)
            changed = True
            skipped = False
        else:
            changed = False
            skipped = True
            meta = {'result': 'skipped'}
    module.exit_json(changed=changed, skipped=skipped, meta=meta)

if __name__ == '__main__':
    main()
