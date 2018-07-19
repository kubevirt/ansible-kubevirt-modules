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
module: kubevirt_facts

short_description: Retrieve facts about KubeVirt resources

description:
  - Retrieve facts about KubeVirt resources

version_added: "2.5"

author: KubeVirt Team (@kubevirt)

options:
    name:
        description:
            - Resource name for which facts will be gathered.
        required: false
    namespace:
        description:
            - Namespace where to look for resources.
            - Required when I(name) is specified.
        required: false
    kind:
        description:
            - Resource type.
            - Must match one of the KubeVirt non-list resource types.
            - See U(https://kubevirt.io/api-reference/master/definitions.html).
        required: true
    api_version:
        description:
            - KubeVirt API version.
        required: false
        default: v1
    label_selectors:
        description:
            - Selector to limit the list of returned objects by their labels.
        required: false
    field_selectors:
        description:
            - Selector to limit the list of returned objects by their fields.
        required: false
    kubeconfig:
        description:
            - "Path to an existing Kubernetes config file. If not provided,
               and no other connection options are provided, the kubernetes
               client will attempt to load the default configuration file
               from C(~/.kube/config.json)."
    context:
        description:
            - The name of a context found in the config file.
    host:
        description:
            - Provide a URL for accessing the API.
    api_key:
        description:
            - Token used to authenticate with the API.
    username:
        description:
            - Provide a username for authenticating with the API.
    password:
        description:
            - Provide a password for authenticating with the API.
    verify_ssl:
        description:
            - Whether or not to verify the API server's SSL certificates.
        default: true
    ssl_ca_cert:
        description:
            - Path to a CA certificate used to authenticate with the API.
    cert_file:
        description:
            - Path to a certificate used to authenticate with the API.
    key_file:
        description:
            - Path to a key file used to authenticate with the API.

requirements:
    - python >= 2.7
    - kubevirt-python >= v0.6.0-177-gd265c3c
'''

EXAMPLES = '''
- name: Facts for testvm in vms namespace
  kubevirt_facts:
      name: testvm
      namespace: vms
      kind: VirtualMachine
  register: testvm_facts
- debug:
      var: testvm_facts

- name: Facts for all VMIs in the cluster
  kubevirt_facts:
      kind: VirtualMachineInstance
  register: all_vmis
- debug:
      var: all_vmis

- name: Facts for all VMIRS in vms namespace
  kubevirt_facts:
      kind: VirtualMachineInstanceReplicaSet
      namespace: vms
  register: all_vms_vmirs
- debug:
      var: all_vms_vmirs

- name: Facts for all VMIS in vms namespace with label 'app = web'
  kubevirt_facts:
      kind: VirtualMachineInstance
      namespace: vms
      label_selector:
          - app = web
  register: all_vmis_app_web
- debug:
      var: all_vmis_app_web
'''

RETURN = '''
items:
  description: "Dictionary describing the requested resource.
                Resource attributes are mapped to dictionary
                keys, which can be found at the following URL:
                U(http://www.kubevirt.io/api-reference/master/definitions.html)"
  returned: On success.
  type: complex
  contains:
      api_version:
          description: The versioned schema of the object representation.
          returned: success
          type: str
      kind:
          description: The REST resource type this object represents.
          returned: success
          type: str
      metadata:
          description: "Metadata includes name, namespace, annotations,
                        labels, etc."
          returned: success
          type: dict
      spec:
          description: "Specific attributes of the object depending
                        on the I(api_version) and I(kind)."
          returned: success
          type: dict
      status:
          description: Current status details for the object.
          returned: success
          type: dict
'''

from ansible.module_utils.k8svirt.facts import KubeVirtFacts


def main():
    """ Entry point. """
    facts = KubeVirtFacts()
    obj = facts.execute_module()

    if 'items' not in obj:
        obj = dict(items=[obj])

    facts.exit_json(
        changed=False,
        ansible_facts=obj
    )


if __name__ == '__main__':
    main()
