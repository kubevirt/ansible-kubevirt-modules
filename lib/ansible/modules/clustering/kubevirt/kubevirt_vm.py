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
    disks:
        description:
            - List of dictionaries which specify disks of the virtual machine.
            - A disk can be made accessible via four different types: I(disk), I(lun), I(cdrom), I(floppy).
            - https://kubevirt.io/api-reference/master/definitions.html#_v1_disk
        type: list
    volumes:
        description:
            - List of volumes specification for the virtual machine.
            - https://kubevirt.io/api-reference/master/definitions.html#_v1_volume
        type: str
    labels:
        description:
            - Labels are key/value pairs that are attached to virtual machines. Labels are intended to be used to
              specify identifying attributes of virtual machines that are meaningful and relevant to users, but do not directly
              imply semantics to the core system. Labels can be used to organize and to select subsets of virtual machines.
              Labels can be attached to virtual machines at creation time and subsequently added and modified at any time.
            - More on labels that are used for internal implementation:
              https://kubevirt.io/user-guide/#/misc/annotations_and_labels
        type: dict
    machine_type:
        description:
            - QEMU machine type is the actual chipset of the virtual machine.
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
          volumeName: registryvolume
          disk:
            bus: virtio

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
          volumeName: registryvolume
          disk:
            bus: virtio
        - name: cloudinitdisk
          volumeName: cloudinitvolume
          disk:
            bus: virtio
      volumes:
        - name: registryvolume
          registryDisk:
            image: kubevirt/cirros-registry-disk-demo:latest
        - name: cloudinitvolume
          cloudInitNoCloud:

- name: Start ephemeral virtual machine 'myvm' and wait to be running
  kubevirt_vm:
      ephemeral: true
      state: running
      wait: true
      wait_time: 20
      name: myvm
      namespace: vms
      memory: 64M
      labels:
        kubevirt.io/vm: myvm
      disks:
        - name: registrydisk
          volumeName: registryvolume
          disk:
            bus: virtio
        - name: cloudinitdisk
          volumeName: cloudinitvolume
          disk:
            bus: virtio
      volumes:
        - name: registryvolume
          registryDisk:
            image: kubevirt/cirros-registry-disk-demo:latest
        - name: cloudinitvolume
          cloudInitNoCloud:
            userDataBase64: IyEvYmluL3NoCgplY2hvICdwcmludGVkIGZyb20gY2xvdWQtaW5pdCB1c2VyZGF0YScK

- name: Remove virtual machine 'myvm'
  kubevirt_vm:
      state: absent
      name: myvm
      namespace: vms
'''

RETURN = '''
vm:
    description:
      - The virtual machine that user manages.
      - It contains all attributes https://kubevirt.io/api-reference/master/definitions.html#_v1_virtualmachine
    returned: success
    type: complex
'''

import copy
import traceback

from collections import defaultdict

from ansible.module_utils.k8s.common import AUTH_ARG_SPEC, COMMON_ARG_SPEC
from ansible.module_utils.k8s.raw import KubernetesRawModule

from openshift import watch
from openshift.dynamic.client import ResourceInstance
from openshift.helper.exceptions import KubernetesException


VM_ARG_SPEC = {
    'merge_type': {'type': 'list', 'choices': ['json', 'merge', 'strategic-merge']},
    'ephemeral': {'type': 'bool', 'default': False},
    'state': {
        'type': 'str',
        'choices': [
            'present', 'absent', 'running', 'stopped'
        ],
        'default': 'present'
    },
    'wait': {'type': 'bool', 'default': True},
    'wait_time': {'type': 'int', 'default': 30},
    'memory': {'type': 'str'},
    'disks': {'type': 'list'},
    'volumes': {'type': 'list'},
    'labels': {'type': 'dict'},
    'machine_type': {'type': 'str'},
}

API_VERSION = 'kubevirt.io/v1alpha2'


def virtdict():
    return defaultdict(virtdict)


class KubeVirtVM(KubernetesRawModule):
    def __init__(self, *args, **kwargs):
        super(KubeVirtVM, self).__init__(*args, **kwargs)

    def merge_dicts(self, x, y):
        z = x.copy()
        z.update(y)
        return z

    @property
    def argspec(self):
        """ argspec property builder """
        argument_spec = copy.deepcopy(COMMON_ARG_SPEC)
        argument_spec.update(copy.deepcopy(AUTH_ARG_SPEC))
        argument_spec.update(VM_ARG_SPEC)
        return argument_spec

    def _manage_state(self, running, resource, existing, wait, wait_time):
        definition = {'metadata': {'name': self.name, 'namespace': self.namespace}, 'spec': {'running': running}}
        self.patch_resource(resource, definition, existing, self.name, self.namespace, merge_type='merge')

        if wait:
            resource = self.find_resource('VirtualMachineInstance', self.api_version, fail=True)
            w, stream = self._create_stream(resource, self.namespace, wait_time)

        if wait and stream is not None:
            self._read_stream(resource, w, stream, self.name, running)

    def _create_stream(self, resource, namespace, wait_time):
        """ Create a stream of events for the object """
        w = None
        stream = None
        try:
            w = watch.Watch()
            w._api_client = self.client.client
            stream = w.stream(resource.get, serialize=False, namespace=namespace, timeout_seconds=wait_time)
        except KubernetesException as exc:
            self.fail_json(msg='Failed to initialize watch: {0}'.format(exc.message))
        return w, stream

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

        self.fail_json(msg="Error waiting for virtual machine. Try a higher wait_time value. %s" % obj.to_dict())

    def get_resource(self, resource):
        try:
            existing = resource.get(name=self.name, namespace=self.namespace)
        except Exception:
            existing = None

        return existing

    def manage_state(self, state):
        wait = self.params.get('wait')
        wait_time = self.params.get('wait_time')
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
                self._manage_state(True, resource_vm, existing, wait, wait_time)
                return True
        elif state == 'stopped':
            if not existing_running:
                return False
            else:
                self._manage_state(False, resource_vm, existing, wait, wait_time)
                return True

    def execute_module(self):
        """ Module execution """
        self.client = self.get_api_client()

        state = self.params.get('state')
        definition = virtdict()
        disks = self.params.get('disks', [])
        volumes = self.params.get('volumes', [])
        memory = self.params.get('memory')
        labels = self.params.get('labels')
        ephemeral = self.params.get('ephemeral')
        machine_type = self.params.get('machine_type')
        template = definition['spec']['template']
        template_spec = template['spec']

        # Merge additional flat parameters:
        if volumes:
            template_spec['volumes'] = volumes

        if disks:
            template_spec['domain']['devices']['disks'] = disks

        if memory:
            template_spec['domain']['resources']['requests']['memory'] = memory

        if labels:
            template['metadata']['labels'] = labels

        if machine_type:
            template_spec['domain']['machine']['type'] = machine_type

        if not ephemeral:
            definition['spec']['running'] = state == 'running'

        # Perform create/absent action:
        definition = self.merge_dicts(self.resource_definitions[0], definition)

        # TODO: Wait for running state in case of ephemeral VM.
        if ephemeral:
            resource = self.find_resource('VirtualMachineInstance', self.api_version, fail=True)
        else:
            resource = self.find_resource('VirtualMachine', self.api_version, fail=True)
        definition = self.set_defaults(resource, definition)
        result = self.perform_action(resource, definition)
        changed = result['changed']

        # Manage the state:
        if state in ['running', 'stopped']:
            if not self.check_mode:
                ret = self.manage_state(state)
                changed = changed or ret

        self.exit_json(**{
            'changed': changed,
            'vm': result,
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
