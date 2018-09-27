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

version_added: "2.8"

author: KubeVirt Team (@kubevirt)

description:
  - "Use Openshift Python SDK to scale up or down KubeVirt
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

extends_documentation_fragment:
  - k8s_auth_options

requirements:
  - python >= 2.7
  - openshift >= 0.6.2
'''

EXAMPLES = '''
- name: Set freyja replicas to 2
  kubevirt_scale_vmirs:
      name: baldr
      namespace: vms
      replicas: 2
'''

RETURN = '''
result:
    description:
        - When replica number is different, otherwise empty.
    returned: success
    type: complex
    contains:
        api_version:
            description: "Version of the schema being used for scaling
                          the defined resource."
            returned: success
            type: str
        kind:
            description: The resource type being scaled.
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
            description: Current number of replicas.
            returned: success
            type: complex
'''

import copy

from ansible.module_utils.k8s.common import AUTH_ARG_SPEC, COMMON_ARG_SPEC
from ansible.module_utils.k8s.raw import KubernetesRawModule

try:
    from openshift import watch
    from openshift.dynamic.client import ResourceInstance
    from openshift.helper.exceptions import KubernetesException
except ImportError as exc:
    class KubernetesException(Exception):
        pass


VMIR_ARG_SPEC = {
    'replicas': {'type': 'int', 'required': True},
    'resource_version': {},
    'wait': {'type': 'bool', 'default': True},
    'wait_timeout': {'type': 'int', 'default': 20}
}


class KubeVirtScaleVMIRS(KubernetesRawModule):
    def __init__(self, *args, **kwargs):
        super(KubeVirtScaleVMIRS, self).__init__(*args, **kwargs)

    def execute_module(self):
        definition = self.resource_definitions[0]

        self.client = self.get_api_client()

        name = definition['metadata']['name']
        namespace = definition['metadata'].get('namespace')
        current_replicas = None
        replicas = self.params.get('replicas')
        resource_version = self.params.get('resource_version')

        wait = self.params.get('wait')
        wait_time = self.params.get('wait_timeout')
        existing = None
        existing_count = None
        return_attributes = dict(changed=False, result=dict())

        resource = self.find_resource('virtualmachineinstancereplicasets', 'kubevirt.io/v1alpha2', fail=True)

        try:
            existing = resource.get(name=name, namespace=namespace)
            return_attributes['result'] = existing.to_dict()
        except KubernetesException as exc:
            self.fail_json(msg='Failed to retrieve requested object: {0}'.format(exc.message),
                           error=exc.value.get('status'))

        if hasattr(existing.spec, 'replicas'):
            existing_count = existing.spec.replicas

        if existing_count is None:
            self.fail_json(msg='Failed to retrieve the available count for the requested object.')

        if resource_version and resource_version != existing.metadata.resourceVersion:
            self.exit_json(**return_attributes)

        if current_replicas is not None and existing_count != current_replicas:
            self.exit_json(**return_attributes)

        if existing_count != replicas:
            return_attributes['changed'] = True
            if not self.check_mode:
                k8s_obj = self.scale(resource, existing, replicas, wait, wait_time)
                return_attributes['result'] = k8s_obj

        self.exit_json(**return_attributes)

    @property
    def argspec(self):
        args = copy.deepcopy(COMMON_ARG_SPEC)
        args.pop('state')
        args.pop('force')
        args.update(AUTH_ARG_SPEC)
        args.update(VMIR_ARG_SPEC)
        return args

    def scale(self, resource, existing_object, replicas, wait, wait_time):
        name = existing_object.metadata.name
        namespace = existing_object.metadata.namespace

        scale_obj = {'metadata': {'name': name, 'namespace': namespace}, 'spec': {'replicas': replicas}}

        return_obj = None
        stream = None

        if wait:
            w, stream = self._create_stream(resource, namespace, wait_time)

        try:
            return_obj, err = self.patch_resource(
                resource, scale_obj, existing_object, name, namespace, merge_type='merge'
            )
            if err:
                raise Exception('Failed to patch resource: {}'.format(err))
        except Exception as exc:
            self.fail_json(
                msg="Scale request failed: {0}".format(exc.message)
            )

        if wait and stream is not None:
            return_obj = self._read_stream(resource, w, stream, name, replicas)

        return return_obj

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

    def _read_stream(self, resource, watcher, stream, name, replicas):
        """ Wait for ready_replicas to equal the requested number of replicas. """
        return_obj = None
        try:
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
        except Exception as exc:
            self.fail_json(msg="Exception reading event stream: {0}".format(exc.message))

        if not return_obj:
            self.fail_json(msg="Error fetching the patched object. Try a higher wait_timeout value.")
        if replicas and return_obj.status.readyReplicas is None:
            self.fail_json(msg="Failed to fetch the number of ready replicas. Try a higher wait_timeout value.")
        if replicas and return_obj.status.readyReplicas != replicas:
            self.fail_json(msg="Number of ready replicas is {0}. Failed to reach {1} ready replicas within "
                               "the wait_timeout period.".format(return_obj.status.ready_replicas, replicas))
        return return_obj.to_dict()


if __name__ == '__main__':
    KubeVirtScaleVMIRS().execute_module()
