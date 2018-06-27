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

version_added: "2.5"

author: KubeVirt Team (@kubevirt)

description:
  - Retrieve facts about KubeVirt resources

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
