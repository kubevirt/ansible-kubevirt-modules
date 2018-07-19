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

description:
    - Use Kubernets Python SDK to manage the state of KubeVirt VirtualMachines.

version_added: "2.5"

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

import kubernetes.client
from ansible.module_utils.basic import AnsibleModule
from kubernetes.client.rest import ApiException
from kubernetes.config import kube_config


def main():
    ''' Entry point. '''

    args = dict({
        'state': dict({
            'default': 'running',
            'choices': list(['running', 'stopped']),
            'type': 'str'
        }),
        'name': dict({'required': True, 'type': 'str'}),
        'namespace': dict({'required': True, 'type': 'str'}),
        'api_version': dict({
            'required': False,
            'default': 'v1alpha2',
            'type': 'str'
        }),
        'verify_ssl': dict({
            'required': False,
            'default': 'yes',
            'type': 'bool'
        })
    })

    module = AnsibleModule(argument_spec=args)
    kube_config.load_kube_config()
    configuration = kubernetes.client.Configuration()

    if not module.params.get('verify_ssl'):
        configuration.verify_ssl = False

    api_client = kubernetes.client.ApiClient(configuration=configuration)
    api_instance = kubernetes.client.CustomObjectsApi(api_client=api_client)
    group = 'kubevirt.io'
    plural = 'virtualmachines'
    version = module.params.get('api_version')
    namespace = module.params.get('namespace')
    name = module.params.get('name')
    state = True if module.params.get('state') == 'running' else False
    body = dict()
    body['spec'] = dict({'running': state})

    try:
        exists = api_instance.get_namespaced_custom_object(
            group, version, namespace, plural, name)
        current_state = exists.get('spec').get('running')

        if current_state == state:
            module.exit_json(changed=False)

        api_response = api_instance.patch_namespaced_custom_object(
            group, version, namespace, plural, name, body)
        module.exit_json(changed=True, result=api_response)
    except ApiException as exc:
        module.fail_json(msg='Failed to manage requested object',
                         error=exc.reason)


if __name__ == '__main__':
    main()
