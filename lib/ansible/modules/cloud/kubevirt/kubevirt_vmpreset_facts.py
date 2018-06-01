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
module: kubevirt_vmpreset_facts

short_description: Retrieve facts about a KubeVirt virtual machine preset

version_added: "2.5"

author: KubeVirt Team (@kubevirt)

description:
  - Retrieve facts about a KubeVirt virtual machine preset

requirements:
  - python >= 2.7
  - kubevirt-python >= 0.4.1-132-g074b4658
'''

EXAMPLES = '''
# Gather facts about a VM called C(testvm) running on the namespace C(vms)
- kubevirt_vmpreset_facts:
    name: testvm
    namespace: vms
- debug:
    var: kubevirt_vmpreset
'''

RETURN = '''
kubevirt_vmpreset:
    description: "Dictionary describing the virtual machine. Virtual Machine
                  attributes are mapped to dictionary keys, which can be found
                  at the following URL:
                  http://www.kubevirt.io/api-reference/master/definitions.html#_v1_virtualmachinepreset"
    returned: On success.
    type: dict
'''

from ansible.module_utils.k8svirt.facts import KubeVirtFacts


def main():
    """ Entry point. """
    facts = KubeVirtFacts(kind='virtual_machine_preset')
    vm = facts.execute_module()
    facts.exit_json(
        changed=False,
        ansible_facts=dict(kubevirt_vmpreset=vm)
    )


if __name__ == '__main__':
    main()
