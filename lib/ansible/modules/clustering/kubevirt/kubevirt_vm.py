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
module: kubevirt_vm

short_description: Manage KubeVirt virtual machine

description:
    - Use Openshift Python SDK to manage the state of KubeVirt virtual machines.

version_added: "2.8"

author: KubeVirt Team (@kubevirt)

options:
    state:
        description:
            - Set the virtual machine to either I(present), I(absent), I(running) or I(stopped).
            - "I(present) - Create or update virtual machine."
            - "I(absent) - Removes virtual machine."
            - "I(running) - Create or update virtual machine and run it."
            - "I(stopped) - Stops the virtual machine."
        default: "present"
        choices:
            - present
            - absent
            - running
            - stopped
        type: str
    name:
        description:
            - Name of the virtual machine.
        required: true
        type: str
    namespace:
        description:
            - Namespace where the virtual machine exists.
        required: true
        type: str
    ephemeral:
        description:
            - If (true) ephemeral vitual machine will be created. When destroyed it won't be accessible again.
            - Works only with C(state) I(present) and I(absent).
        type: bool
        default: false

extends_documentation_fragment:
  - k8s_auth_options
  - k8s_resource_options
  - kubevirt_vm_options

requirements:
  - python >= 2.7
  - openshift >= 0.6.2
'''

EXAMPLES = '''
- name: Start virtual machine 'myvm'
  kubevirt_vm:
      state: running
      name: myvm
      namespace: vms

- name: Create virtual machine 'myvm' and start it
  kubevirt_vm:
      state: running
      name: myvm
      namespace: vms
      memory: 64M
      disks:
        - name: registrydisk
          volume:
            registryDisk:
              image: kubevirt/cirros-registry-disk-demo:latest
          disk:
            bus: virtio

- name: Create virtual machine 'myvm' with multus network interface
  kubevirt_vm:
      name: myvm
      namespace: vms
      memory: 512M
      interfaces:
        - name: default
          bridge: {}
          network:
            pod: {}
        - name: mynet
          bridge: {}
          network:
            multus:
              networkName: mynetconf

- name: Combine inline definition with Ansible parameters:
  kubevirt_vm:
      # Kubernetes specification:
      definition:
        metadata:
          labels:
            app: galaxy
            service: web
            origin: vmware

      # Ansible parameters:
      state: running
      name: myvm
      namespace: vms
      memory: 64M
      disks:
        - name: registrydisk
          volume:
            registryDisk:
              image: kubevirt/cirros-registry-disk-demo:latest
          disk:
            bus: virtio

- name: Start ephemeral virtual machine 'myvm' and wait to be running
  kubevirt_vm:
      ephemeral: true
      state: running
      wait: true
      wait_timeout: 180
      name: myvm
      namespace: vms
      memory: 64M
      labels:
        kubevirt.io/vm: myvm
      disks:
        - name: registrydisk
          volume:
            registryDisk:
              image: kubevirt/cirros-registry-disk-demo:latest
          disk:
            bus: virtio

- name: Start fedora vm with cloud init
  kubevirt_vm:
      state: running
      wait: true
      name: myvm
      namespace: vms
      memory: 1024M
      cloud_init_nocloud:
        userData: |-
          password: fedora
          chpasswd: { expire: False }
      disks:
        - name: registrydisk
          volume:
            registryDisk:
              image: kubevirt/fedora-cloud-registry-disk-demo:latest
          disk:
            bus: virtio

- name: Remove virtual machine 'myvm'
  kubevirt_vm:
      state: absent
      name: myvm
      namespace: vms
'''

RETURN = '''
kubevirt_vm:
  description:
    - The virtual machine managed by the user.
  returned: success
  type: complex
  contains:
    k8s_objects:
      description:
      - Lists kubernetes objects this module created, modified or read during operation, by type name.
      returned: success
      type: dict
'''


import copy
import traceback

from ansible.module_utils.k8s.common import AUTH_ARG_SPEC, COMMON_ARG_SPEC

from openshift.dynamic.client import ResourceInstance

import sys
if hasattr(sys, '_called_from_test'):
    sys.path.append('lib/ansible/module_utils')
    import kubevirt
    print kubevirt
    from kubevirt import (
        virtdict,
        VM_COMMON_ARG_SPEC,
        API_VERSION,
        KubeVirtRawModule,
    )
else:
    from ansible.module_utils.kubevirt import (
        virtdict,
        KubeVirtRawModule,
        VM_COMMON_ARG_SPEC,
        API_VERSION,
    )


VM_ARG_SPEC = {
    'ephemeral': {'type': 'bool', 'default': False},
    'state': {
        'type': 'str',
        'choices': [
            'present', 'absent', 'running', 'stopped'
        ],
        'default': 'present'
    },
}


class KubeVirtVM(KubeVirtRawModule):

    @property
    def argspec(self):
        """ argspec property builder """
        argument_spec = copy.deepcopy(COMMON_ARG_SPEC)
        argument_spec.update(copy.deepcopy(AUTH_ARG_SPEC))
        argument_spec.update(VM_COMMON_ARG_SPEC)
        argument_spec.update(VM_ARG_SPEC)
        return argument_spec

    def _manage_state(self, running, resource, existing, wait, wait_timeout):
        definition = {'metadata': {'name': self.name, 'namespace': self.namespace}, 'spec': {'running': running}}
        self.patch_resource(resource, definition, existing, self.name, self.namespace, merge_type='merge')

        if wait:
            resource = self.find_resource('VirtualMachineInstance', self.api_version, fail=True)
            w, stream = self._create_stream(resource, self.namespace, wait_timeout)

        if wait and stream is not None:
            self._read_stream(resource, w, stream, self.name, running)

    def _read_stream(self, resource, watcher, stream, name, running):
        """ Wait for ready_replicas to equal the requested number of replicas. """
        for event in stream:
            if event.get('object'):
                obj = ResourceInstance(resource, event['object'])
                if running:
                    if obj.metadata.name == name and hasattr(obj, 'status'):
                        phase = getattr(obj.status, 'phase', None)
                        if phase:
                            if phase == 'Running' and running:
                                watcher.stop()
                                return
                else:
                    # TODO: wait for stopped state:
                    watcher.stop()
                    return

        self.fail_json(msg="Error waiting for virtual machine. Try a higher wait_timeout value. %s" % obj.to_dict())

    def manage_state(self, state):
        wait = self.params.get('wait')
        wait_timeout = self.params.get('wait_timeout')
        resource_version = self.params.get('resource_version')

        resource_vm = self.find_resource('VirtualMachine', self.api_version)
        existing = self.get_resource(resource_vm)
        if resource_version and resource_version != existing.metadata.resourceVersion:
            return False

        existing_running = False
        resource_vmi = self.find_resource('VirtualMachineInstance', self.api_version)
        existing_running_vmi = self.get_resource(resource_vmi)
        if existing_running_vmi and hasattr(existing_running_vmi.status, 'phase'):
            existing_running = existing_running_vmi.status.phase == 'Running'

        if state == 'running':
            if existing_running:
                return False
            else:
                self._manage_state(True, resource_vm, existing, wait, wait_timeout)
                return True
        elif state == 'stopped':
            if not existing_running:
                return False
            else:
                self._manage_state(False, resource_vm, existing, wait, wait_timeout)
                return True

    def execute_module(self):
        # Parse parameters specific for this module:
        definition = virtdict()
        ephemeral = self.params.get('ephemeral')
        state = self.params.get('state')

        if not ephemeral:
            definition['spec']['running'] = state == 'running'

        # Execute the CURD of VM:
        template = definition['spec']['template']
        kind = 'VirtualMachineInstance' if ephemeral else 'VirtualMachine'
        result = self.execute_crud(kind, definition, template)
        changed = result['changed']

        # Manage state of the VM:
        if state in ['running', 'stopped']:
            if not self.check_mode:
                ret = self.manage_state(state)
                changed = changed or ret

        # Return from the module:
        self.exit_json(**{
            'changed': changed,
            'kubevirt_vm': result.pop('result'),
            'result': result,
        })


def main():
    module = KubeVirtVM()
    try:
        module.api_version = API_VERSION
        module.execute_module()
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()
