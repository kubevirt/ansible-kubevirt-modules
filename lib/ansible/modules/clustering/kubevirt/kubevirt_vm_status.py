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
module: kubevirt_vm_status

short_description: Manage KubeVirt virtual machine state

description:
    - Use Openshift Python SDK to manage the state of KubeVirt VirtualMachines.

version_added: "2.8"

author: KubeVirt Team (@kubevirt)

options:
    state:
        description:
            - Set the VirtualMachine to either (C(running)) or (C(stopped)).
        required: false
        default: "running"
        choices:
            - running
            - stopped
        type: str
    name:
        description:
            - Name of the VirtualMachine.
        required: true
        type: str
    namespace:
        description:
            - Namespace where the VirtualMachine exists.
        required: true
        type: str

extends_documentation_fragment:
  - k8s_auth_options

requirements:
  - python >= 2.7
  - openshift >= 0.6.2
'''

EXAMPLES = '''
- name: Set baldr VM running
  kubevirt_vm_status:
      state: running
      name: baldr
      namespace: vms
'''

RETURN = '''
result:
    description:
        - When replica number is different, otherwise empty.
    returned: success
    type: complex
    contains:
        api_version:
            description: "Version of the schema being used for managing
                          the defined resource."
            returned: success
            type: str
        kind:
            description: The resource type being managed.
            returned: success
            type: str
        metadata:
            description: Standard resource metadata, e.g. name, namespace, etc.
            returned: success
            type: complex
        spec:
            description: "Set of resource attributes, can vary based
                          on the I(api_version)."
            returned: success
            type: complex
        status:
            description: Current status details for the resource.
            returned: success
            type: complex
'''
import copy
import traceback

from ansible.module_utils.k8s.common import AUTH_ARG_SPEC, COMMON_ARG_SPEC
from ansible.module_utils.k8s.raw import KubernetesRawModule

try:
    from openshift.helper.exceptions import KubernetesException
except ImportError as exc:
    class KubernetesException(Exception):
        pass


VM_ARG_SPEC = {
    'state': {'type': 'str', 'required': True, 'choices': ['running', 'stopped']},
}


class KubeVirtVMStatus(KubernetesRawModule):
    def __init__(self, *args, **kwargs):
        super(KubeVirtVMStatus, self).__init__(*args, **kwargs)

    @property
    def argspec(self):
        """ argspec property builder """
        argument_spec = copy.deepcopy(COMMON_ARG_SPEC)
        argument_spec.update(copy.deepcopy(AUTH_ARG_SPEC))
        argument_spec.update(VM_ARG_SPEC)
        return argument_spec

    def _manage_state(self, running, name, namespace, resource, existing, return_attributes):
        return_attributes['changed'] = True
        if not self.check_mode:
            definition = {'metadata': {'name': name, 'namespace': namespace}, 'spec': {'running': running}}
            k8s_obj, error = self.patch_resource(resource, definition, existing, name,
                                                 namespace, merge_type='merge')
            if not error:
                return_attributes['result'] = k8s_obj

    def execute_module(self):
        """ Module execution """
        definition = self.resource_definitions[0]
        self.client = self.get_api_client()

        state = self.params.get('state')
        resource_version = self.params.get('resource_version')
        name = definition['metadata']['name']
        namespace = definition['metadata'].get('namespace')
        api_version = self.params.get('apiVersion', 'kubevirt.io/v1alpha2')

        existing = None
        existing_running = None
        return_attributes = dict(changed=False, result=dict())

        resource = self.find_resource('VirtualMachine', api_version, fail=True)

        try:
            existing = resource.get(name=name, namespace=namespace)
            return_attributes['result'] = existing.to_dict()
        except KubernetesException as exc:
            self.fail_json(msg='Failed to retrieve requested object: {0}'.format(exc.message),
                           error=exc.value.get('status'))

        if hasattr(existing.spec, 'running'):
            existing_running = existing.spec.running

        if resource_version and resource_version != existing.metadata.resourceVersion:
            self.exit_json(**return_attributes)

        if state == 'running':
            if existing_running:
                self.exit_json(**return_attributes)
            else:
                self._manage_state(True, name, namespace, resource, existing, return_attributes)
        elif state == 'stopped':
            if not existing_running:
                self.exit_json(**return_attributes)
            else:
                self._manage_state(False, name, namespace, resource, existing, return_attributes)

        self.exit_json(**return_attributes)


def main():
    module = KubeVirtVMStatus()
    try:
        module.execute_module()
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()
