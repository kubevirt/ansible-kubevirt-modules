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

short_description: Manage KubeVirt VM state

version_added: "2.5"

author: KubeVirt Team (@kubevirt)

description:
  - Use Kubernets Python SDK to manage the state of KubeVirt VirtualMachines.

options:
    state:
        description:
            - Set the VirtualMachine to either (C(running)) or (C(stopped)).
        required: false
        default: "running"
        choices: ["running", "stopped"]
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
    api_version:
        description:
            - KubeVirt API version to use.
        required: false
        type: str
        default: v1alpha2
    verify_ssl:
        description:
            - Whether to verify SSL certificate.
        required: false
        type: bool
        default: yes

requirements:
  - python >= 2.7
  - kubernetes python client >= 6.0.0
'''

EXAMPLES = '''
- name: Set baldr VM running
  kubevirt_vm_status:
    state: running
    name: baldr
    namespace: vms
'''

RETURN = ''' # '''

import copy

from ansible.module_utils.k8svirt.helper import to_snake, COMMON_ARG_SPEC,\
    AUTH_ARG_SPEC, get_helper
from ansible.module_utils.k8svirt.common import K8sVirtAnsibleModule
from kubevirt.rest import ApiException


class KubeVirtVMState(K8sVirtAnsibleModule):
    """ Class for managing a VM state """
    def __init__(self, *args, **kwargs):
        """ Class constructor """
        super(KubeVirtVMState, self).__init__(
            *args, supports_check_mode=False, **kwargs)
        self._api_client = None
        self._kind = self.params.pop('VirtualMachine')

    @property
    def argspec(self):
        """ Merge the module arguments """
        argspec = copy.deepcopy(COMMON_ARG_SPEC)
        argspec.update(copy.deepcopy(AUTH_ARG_SPEC))
        argspec['state'] = dict({
            'default': 'running',
            'choices': list(['running', 'stopped']),
            'type': 'str'
        })
        return argspec

    def execute_modules(self):
        """ # """
        self._api_client = self.authenticate()
        state = True if self.params.get('state') == 'running' else False
        body = dict()
        body['spec'] = dict({'running': state})
        name = self.params.get('name')
        namespace = self.params.get('namespace')
        helper = get_helper(self._api_client, self._kind)
        try:
            current_vm = helper.exists(name, namespace)
            current_state = current_vm.get('spec').get('running')
            desired_state = body.get('spec').get('running')
            if current_state == desired_state:
                self.exit_json(changed=False)
            helper.patch(
                body, self.params.get('namespace'), self.params.get('name'))
        except ApiException as exc:
            self.fail_json(
                msg='Failed to manage the VM state', error=exc.reason)


#import kubernetes.client
#from ansible.module_utils.basic import AnsibleModule
#from kubernetes.client.rest import ApiException
#from kubernetes.config import kube_config
#
#
#def main():
#    ''' Entry point. '''
#
#    args = dict({
#        'state': dict({
#            'default': 'running',
#            'choices': list(['running', 'stopped']),
#            'type': 'str'
#        }),
#        'name': dict({'required': True, 'type': 'str'}),
#        'namespace': dict({'required': True, 'type': 'str'}),
#        'api_version': dict({
#            'required': False,
#            'default': 'v1alpha2',
#            'type': 'str'
#        }),
#        'verify_ssl': dict({
#            'required': False,
#            'default': 'yes',
#            'type': 'bool'
#        })
#    })
#
#    module = AnsibleModule(argument_spec=args)
#    kube_config.load_kube_config()
#    configuration = kubernetes.client.Configuration()
#
#    if not module.params.get('verify_ssl'):
#        configuration.verify_ssl = False
#
#    api_client = kubernetes.client.ApiClient(configuration=configuration)
#    api_instance = kubernetes.client.CustomObjectsApi(api_client=api_client)
#    group = 'kubevirt.io'
#    plural = 'virtualmachines'
#    version = module.params.get('api_version')
#    namespace = module.params.get('namespace')
#    name = module.params.get('name')
#    state = True if module.params.get('state') == 'running' else False
#    body = dict()
#    body['spec'] = dict({'running': state})
#
#    try:
#        exists = api_instance.get_namespaced_custom_object(
#            group, version, namespace, plural, name)
#        current_state = exists.get('spec').get('running')
#
#        if current_state == state:
#            module.exit_json(changed=False)
#
#        api_response = api_instance.patch_namespaced_custom_object(
#            group, version, namespace, plural, name, body)
#        module.exit_json(changed=True, meta=api_response)
#    except ApiException as exc:
#        module.fail_json(msg='Failed to manage requested object',
#                         error=exc.reason)


if __name__ == '__main__':
    main()
