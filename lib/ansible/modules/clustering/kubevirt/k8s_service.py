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
module: k8s_service

short_description: Manage Services on Kubernetes

description:
    - Use Openshift Python SDK to manage Services on Kubernetes

version_added: "2.8"

author: KubeVirt Team (@kubevirt)

options:
    name:
        description:
            - Use to specify a Service object name.
        required: true
        type: str
    namespace:
        description:
            - Use to specify a Service object namespace.
        required: true
        type: str
    type:
        description:
            - Specifies the type of Service to create.
            - U(https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types)
        choices:
            - NodePort
            - ClusterIP
            - LoadBalancer
            - ExternalName
        default: ClusterIP
        required: true
    ports:
        description:
            - A list of ports to expose.
            - U(https://kubernetes.io/docs/concepts/services-networking/service/#multi-port-services)
        required: true
        type: list
    selector:
        description:
            - Label selectors identify objects this Service should apply to.
            - U(https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)
        required: true
        type: dict

extends_documentation_fragment:
  - k8s_auth_options
  - k8s_resource_options

requirements:
  - python >= 2.7
  - openshift >= 0.6.2
'''

EXAMPLES = '''
- name: Expose https port with ClusterIP
  k8s_service:
    state: present
    name: test-https
    namespace: default
    type: ClusterIP
    ports:
    - port: 443
      protocol: TCP
    selector:
      key: special
'''

RETURN = '''
result:
  description:
  - The created, patched, or otherwise present Service object. Will be empty in the case of a deletion.
  returned: success
  type: complex
  contains:
     api_version:
       description: The versioned schema of this representation of an object.
       returned: success
       type: str
     kind:
       description: Always 'Service'.
       returned: success
       type: str
     metadata:
       description: Standard object metadata. Includes name, namespace, annotations, labels, etc.
       returned: success
       type: complex
     spec:
       description: Specific attributes of the object. Will vary based on the I(api_version) and I(kind).
       returned: success
       type: complex
     status:
       description: Current status details for the object.
       returned: success
       type: complex
     items:
       description: Returned only when multiple yaml documents are passed to src or resource_definition
       returned: when resource_definition or src contains list of objects
       type: list
'''

import copy
import traceback

from collections import defaultdict

from ansible.module_utils.k8s.common import AUTH_ARG_SPEC, COMMON_ARG_SPEC
from ansible.module_utils.k8s.raw import KubernetesRawModule


SERVICE_ARG_SPEC = {
    'merge_type': {'type': 'list', 'choices': ['json', 'merge', 'strategic-merge']},
    'selector': {'type': 'dict'},
    'type': {
        'type': 'str',
        'choices': [
            'NodePort', 'ClusterIP', 'LoadBalancer', 'ExternalName'
        ],
        'default': 'ClusterIP',
    },
    'ports': {'type': 'list'},
}

API_VERSION = 'v1'


def virtdict():
    return defaultdict(virtdict)


class KubernetesService(KubernetesRawModule):
    def __init__(self, *args, **kwargs):
        super(KubernetesService, self).__init__(*args, **kwargs)

    @staticmethod
    def merge_dicts(x, y):
        for k in set(x.keys()).union(y.keys()):
            if k in x and k in y:
                if isinstance(x[k], dict) and isinstance(y[k], dict):
                    yield (k, dict(KubernetesService.merge_dicts(x[k], y[k])))
                else:
                    yield (k, y[k])
            elif k in x:
                yield (k, x[k])
            else:
                yield (k, y[k])

    @property
    def argspec(self):
        """ argspec property builder """
        argument_spec = copy.deepcopy(COMMON_ARG_SPEC)
        argument_spec.update(copy.deepcopy(AUTH_ARG_SPEC))
        argument_spec.update(SERVICE_ARG_SPEC)
        return argument_spec

    def execute_module(self):
        """ Module execution """
        self.client = self.get_api_client()

        selector = self.params.get('selector')
        service_type = self.params.get('type')
        ports = self.params.get('ports')

        definition = virtdict()

        def_spec = definition['spec']
        def_spec['type'] = service_type
        def_spec['ports'] = ports
        def_spec['selector'] = selector

        # Override with 'resource_definition:' if provided
        definition = dict(self.merge_dicts(definition, self.resource_definitions[0]))

        resource = self.find_resource('Service', self.api_version, fail=True)
        definition = self.set_defaults(resource, definition)
        result = self.perform_action(resource, definition)

        self.exit_json(**result)


def main():
    module = KubernetesService()
    try:
        module.api_version = API_VERSION
        module.execute_module()
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()
