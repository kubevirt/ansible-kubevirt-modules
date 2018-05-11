#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0
# (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''

module: kubevirt_raw

short_description: Manage KubeVirt objects

version_added: "2.5"

author: KubeVirt Team (@kubevirt)

description:
  - Use KubeVirt Python SDK to perform CRUD operations on KubeVirt objects.
  - Pass the object definition from a source file or inline.
  - Authenticate using either a config file, certificates, password or token.

extends_documentation_fragment:


requirements:
  - python >= 2.7
  - kubevirt-python >= 0.4.1-132-g074b4658
'''

EXAMPLES = '''
- name: Create a VM from a source file
  kubevirt_raw:
    state: present
    src: /testing/vm.yml
'''

RETURN = ''' # '''

from ansible.module_utils.k8svirt.raw import KubeVirtRawModule


def main():
    '''Entry point.'''
    KubeVirtRawModule().execute_module()


if __name__ == '__main__':
    main()
