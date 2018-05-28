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
module: kubevirt_vm_facts

short_description: Retrieve facts about a KubeVirt virtual machine replica set

version_added: "2.5"

author: KubeVirt Team (@kubevirt)

description:
  - Retrieve facts about a KubeVirt virtual machine replica set

requirements:
  - python >= 2.7
  - kubevirt-python >= 0.4.1-132-g074b4658
'''

EXAMPLES = '''
# Gather facts about a VMRS called C(testvm) running on the namespace C(vms)
- kubevirt_vmrs_facts:
    name: testvmrs
    namespace: vms
- debug:
    var: kubevirt_vmrs
'''

RETURN = '''
kubevirt_vmrs:
    description: "Dictionary describing the virtual machine. Virtual Machine
                  attributes are mapped to dictionary keys, which can be found
                  at the following URL:
                  http://www.kubevirt.io/api-reference/master/definitions.html#_v1_virtualmachinereplicaset"
    returned: On success.
    type: dict
'''

from ansible.module_utils.k8svirt.facts import KubeVirtFacts


def main():
    """ Entry point. """
    facts = KubeVirtFacts(kind='virtual_machine_replica_set')
    vmrs = facts.execute_module()
    facts.exit_json(
        changed=False,
        ansible_facts=dict(kubevirt_vmrs=vmrs)
    )


if __name__ == '__main__':
    main()
