#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0
# (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: kubevirt_rs

short_description: Manage KubeVirt virtual machine replica sets

description:
    - Use Openshift Python SDK to manage the state of KubeVirt virtual machine replica stes.

version_added: "2.8"

author: KubeVirt Team (@kubevirt)

options:
    state:
        description:
            - Create or delete virtua machine replica sets.
        default: "present"
        choices:
            - present
            - absent
        type: str
    name:
        description:
            - Name of the virtual machine replica set.
        required: true
        type: str
    namespace:
        description:
            - Namespace where the virtual machine replica set exists.
        required: true
        type: str
    selector:
        description:
            - "Selector is a label query over a set of virtual machine."
        required: true
        type: dict
    replicas:
        description:
            - ""Number of desired pods. This is a pointer to distinguish between explicit zero and not specified. Defaults to 1."
        type: int
        default: 1

extends_documentation_fragment:
  - k8s_auth_options
  - k8s_resource_options
  - kubevirt_vm_options

requirements:
  - python >= 2.7
  - openshift >= 0.6.2
'''

EXAMPLES = '''
- name: Create virtual machine replica set 'myvmir'
  kubevirt_rs:
      state: presnet
      name: myvmir
      namespace: vms
      wait: true
      replicas: 3
      memory: 64M
      labels:
        myvmi: myvmi
      selector:
        matchLabels:
            myvmi: myvmi
      disks:
         - name: registrydisk
           volume:
             registryDisk:
               image: kubevirt/cirros-registry-disk-demo:latest
           disk:
             bus: virtio

- name: Remove virtual machine replica set 'myvmir'
  kubevirt_rs:
      state: absent
      name: myvmir
      namespace: vms
      wait: true
'''

RETURN = '''
kubevirt_rs:
  description:
    - The virtual machine virtual machine replica set managed by the user.
    - "This dictionary contains all values returned by the KubeVirt API all options
       are described here U(https://kubevirt.io/api-reference/master/definitions.html#_v1_virtualmachineinstance)"
  returned: success
  type: dict
'''

import copy
import traceback


from ansible.module_utils.k8s.common import AUTH_ARG_SPEC, COMMON_ARG_SPEC

from openshift.dynamic.client import ResourceInstance

# FIXME:
import sys
if hasattr(sys, '_called_from_test'):
    sys.path.append('lib/ansible/module_utils/')
    from kubevirt import (
        virtdict,
        VM_COMMON_ARG_SPEC,
        API_VERSION,
        KubeVirtRawModule,
    )
else:
    from ansible.module_utils.kubevirt import (
        virtdict,
        VM_COMMON_ARG_SPEC,
        API_VERSION,
        KubeVirtRawModule,
    )


KIND = 'VirtualMachineInstanceReplicaSet'
VMIR_ARG_SPEC = {
    'replicas': {'type': 'int', 'required': True},
    'selector': {'type': 'dict'},
}


class KubeVirtVMIRS(KubeVirtRawModule):

    @property
    def argspec(self):
        """ argspec property builder """
        argument_spec = copy.deepcopy(COMMON_ARG_SPEC)
        argument_spec.update(copy.deepcopy(AUTH_ARG_SPEC))
        argument_spec.update(VM_COMMON_ARG_SPEC)
        argument_spec.update(VMIR_ARG_SPEC)
        return argument_spec

    def _read_stream(self, resource, watcher, stream, name, replicas):
        """ Wait for ready_replicas to equal the requested number of replicas. """
        return_obj = None
        for event in stream:
            if event.get('object'):
                obj = ResourceInstance(resource, event['object'])
                if obj.metadata.name == name and hasattr(obj, 'status'):
                    if replicas == 0:
                        if not hasattr(obj.status, 'readyReplicas') or not obj.status.readyReplicas:
                            return_obj = obj
                            watcher.stop()
                            break
                    if hasattr(obj.status, 'readyReplicas') and obj.status.readyReplicas == replicas:
                        return_obj = obj
                        watcher.stop()
                        break

        if not return_obj:
            self.fail_json(msg="Error fetching the patched object. Try a higher wait_timeout value.")
        if replicas and return_obj.status.readyReplicas is None:
            self.fail_json(msg="Failed to fetch the number of ready replicas. Try a higher wait_timeout value.")
        if replicas and return_obj.status.readyReplicas != replicas:
            self.fail_json(msg="Number of ready replicas is {0}. Failed to reach {1} ready replicas within "
                               "the wait_timeout period.".format(return_obj.status.ready_replicas, replicas))
        return return_obj.to_dict()

    def wait_for_replicas(self):
        namespace = self.params.get('namespace')
        wait_time = self.params.get('wait_time')
        replicas = self.params.get('replicas')
        name = self.name
        resource = self.find_resource(KIND, self.api_version, fail=True)

        w, stream = self._create_stream(resource, namespace, wait_time)
        return self._read_stream(resource, w, stream, name, replicas)

    def execute_module(self):
        # Parse parameters specific for this module:
        definition = virtdict()
        selector = self.params.get('selector')
        replicas = self.params.get('replicas')

        if selector:
            definition['spec']['selector'] = selector

        if replicas is not None:
            definition['spec']['replicas'] = replicas

        # Execute the CURD of VM:
        result_crud = self.execute_crud(KIND, definition)
        changed = result_crud['changed']
        result = result_crud.pop('result')

        # Wait for the replicas:
        wait = self.params.get('wait')
        if wait:
            result = self.wait_for_replicas()

        # Return from the module:
        self.exit_json(**{
            'changed': changed,
            'kubevirt_rs': result,
            'result': result_crud,
        })


def main():
    module = KubeVirtVMIRS()
    try:
        module.api_version = API_VERSION
        module.execute_module()
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()
