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
module: kubevirt_ovm_facts

short_description: Retrieve facts about a KubeVirt offline virtual machine

version_added: "2.5"

author: KubeVirt Team (@kubevirt)

description:
  - Retrieve facts about a KubeVirt offline virtual machine

requirements:
  - python >= 2.7
  - kubevirt-python >= 0.4.1-132-g074b4658
'''

EXAMPLES = '''
# Gather facts about an Offline VM called C(testvm) created
# on the namespace C(vms)
- kubevirt_ovm_facts:
    name: testovm
    namespace: vms
- debug:
    var: kubevirt_ovm
'''

RETURN = '''
kubevirt_ovm:
    description: "Dictionary describing the offline virtual machine.
                  Offline Virtual Machine attributes are mapped to dictionary
                  keys, which can be found at the following URL:
                  http://www.kubevirt.io/api-reference/master/definitions.html#_v1_offlinevirtualmachine"
    returned: On success.
    type: dict
'''

from ansible.module_utils.k8svirt.facts import KubeVirtFacts


def main():
    """ Entry point. """
    facts = KubeVirtFacts(kind='offline_virtual_machine')
    ovm = facts.execute_module()
    facts.exit_json(
        changed=False,
        ansible_facts=dict(kubevirt_ovm=ovm)
    )


if __name__ == '__main__':
    main()
