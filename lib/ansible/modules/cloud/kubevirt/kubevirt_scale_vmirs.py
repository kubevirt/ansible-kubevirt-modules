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
module: kubevirt_scale_vmirs

short_description: Scale up or down KubeVirt VMI ReplicaSet

version_added: "2.5"

author: KubeVirt Team (@kubevirt)

description:
  - "Use Kubernets Python SDK to scale up or down KubeVirt
     VirtualMachineInstance ReplicaSet."

options:
    name:
        description:
            - Name of the VirtualMachineInstance ReplicaSet.
        required: true
        type: str
    namespace:
        description:
            - Namespace where the VirtualMachineInstance ReplicaSet exists.
        required: true
        type: str
    replicas:
        description:
            - Number of replicas to be currently present.
        required: true
        type: int
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
- name: Set freyja replicas to 2
  kubevirt_scale_vmirs:
    name: baldr
    namespace: vms
    replicas: 2
'''

RETURN = ''' # '''

import kubernetes.client
from ansible.module_utils.basic import AnsibleModule
from kubernetes.client.rest import ApiException
from kubernetes.config import kube_config


def main():
    ''' Entry point. '''

    args = dict({
        'name': dict({'required': True, 'type': 'str'}),
        'namespace': dict({'required': True, 'type': 'str'}),
        'replicas': dict({'required': True, 'type': 'int'}),
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
    plural = 'virtualmachineinstancereplicasets'
    version = module.params.get('api_version')
    namespace = module.params.get('namespace')
    name = module.params.get('name')
    body = dict()
    body['spec'] = dict({'replicas': module.params.get('replicas')})

    try:
        exists = api_instance.get_namespaced_custom_object(
            group, version, namespace, plural, name)
        current = exists.get('spec').get('replicas')

        if current == module.params.get('replicas'):
            module.exit_json(changed=False)

        api_response = api_instance.patch_namespaced_custom_object(
            group, version, namespace, plural, name, body)
        module.exit_json(changed=True, meta=api_response)
    except ApiException as exc:
        module.fail_json(msg='Failed to manage requested object',
                         error=exc.reason)


if __name__ == '__main__':
    main()
