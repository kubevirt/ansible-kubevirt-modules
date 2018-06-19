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
module: kubevirt_vmi_facts

short_description: Retrieve facts about a KubeVirt virtual machine instance

version_added: "2.5"

author: KubeVirt Team (@kubevirt)

description:
  - Retrieve facts about a KubeVirt virtual machine instance

requirements:
  - python >= 2.7
  - kubevirt-python >= v0.6.0-177-gd265c3c
'''

EXAMPLES = '''
# Gather facts about a VMI called C(testvm) running on the namespace C(vms)
- kubevirt_vmi_facts:
    name: testvm
    namespace: vms
- debug:
    var: kubevirt_vmi
'''

RETURN = '''
kubevirt_vmi:
    description: "Dictionary describing the virtual machine instance. Virtual
                  Machine Instance attributes are mapped to dictionary keys,
                  which can be found at the following URL:
                  U(http://www.kubevirt.io/api-reference/master/definitions.html#_v1_virtualmachineinstance)"
    returned: On success.
    type: dict
'''

from ansible.module_utils.k8svirt.facts import KubeVirtFacts


def main():
    """ Entry point. """
    facts = KubeVirtFacts(kind='virtual_machine_instance')
    vmi = facts.execute_module()
    facts.exit_json(
        changed=False,
        ansible_facts=dict(kubevirt_vmi=vmi)
    )


if __name__ == '__main__':
    main()
