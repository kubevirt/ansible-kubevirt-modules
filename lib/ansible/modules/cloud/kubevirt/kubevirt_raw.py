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

description:
    - Use KubeVirt Python SDK to perform CRUD operations on KubeVirt objects.
    - Pass the object definition from a source file or inline.
    - Authenticate using either a config file, certificates, password or token.

version_added: "2.5"

author: KubeVirt Team (@kubevirt)

options:
    state:
        description:
            - "Define the resource state, wether created C(present)
               or deleted C(absent)."
        required: false
        default: present
        choices:
            - present
            - absent
    force:
        description:
            - "When C(true) or C(yes), together with I(state=present),
               the defined resource will be forcefully replaced."
        required: false
        default: false
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
    resource_definition:
        description:
            - Provide an inline valid YAML for KubeVirt resource.
            - Required when I(state=present).
            - Mutually exclusive with I(src).
        required: false
    src:
        description:
            - Provide a valid YAML definition, loading it from a file.
            - Mutually exclusive with I(resource_definition).
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
            - "Required if I(api_key) or I(username) and I(password) are
               specified."
    api_key:
        description:
            - Token used to authenticate with the API.
            - To be used together with I(host).
    username:
        description:
            - Provide a username for authenticating with the API.
            - To be used together with I(host) and I(password).
    password:
        description:
            - Provide a password for authenticating with the API.
            - To be used together with I(host) and I(username).
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
    - kubevirt-python >= 0.4.1-132-g074b4658
'''

EXAMPLES = '''
- name: Create a VM from a source file
  kubevirt_raw:
      state: present
      src: /testing/vm.yml

- name: Create VM defined inline
  kubevirt_raw:
      state: present
      name: testvm
      namespace: vms
      verify_ssl: no
      inline:
          apiVersion: kubevirt.io/v1alpha2
          kind: VirtualMachine
          metadata:
            name: testvm
          spec:
            running: false
            selector:
              matchLabels:
                guest: testvm
            template:
              metadata:
                labels:
                  guest: testvm
                  kubevirt.io/size: small
              spec:
                domain:
                  resources:
                    requests:
                      memory: 64M
                  devices:
                    disks:
                      - name: registrydisk
                        volumeName: registryvolume
                        disk:
                          bus: virtio
                      - name: cloudinitdisk
                        volumeName: cloudinitvolume
                        disk:
                          bus: virtio
                volumes:
                  - name: registryvolume
                    registryDisk:
                      image: kubevirt/cirros-registry-disk-demo
                  - name: cloudinitvolume
                    cloudInitNoCloud:
                      userDataBase64: SGkuXG4=
'''

RETURN = '''
result:
    description:
        - When creating or updating a resource. Otherwise empty.
    returned: success
    type: complex
    contains:
        api_version:
            description: "Version of the schema being used for managing
                          the defined resource."
            returned: success
            type: str
        kind:
            description: The resource type being managed.
            returned: success
            type: str
        metadata:
            description: Standard resource metadata, e.g. name, namespace, etc.
            returned: success
            type: complex
        spec:
            description: "Set of resource attributes, can vary based
                          on the I(api_version) and I(kind)."
            returned: success
            type: complex
        status:
            description: Current status details for the resource.
            returned: success
            type: complex
'''

from ansible.module_utils.k8svirt.raw import KubeVirtRawModule


def main():
    '''Entry point.'''
    KubeVirtRawModule().execute_module()


if __name__ == '__main__':
    main()
