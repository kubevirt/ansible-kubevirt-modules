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
module: kubevirt_vm_status

short_description: Manage KubeVirt VM state

description:
    - Use Kubernets Python SDK to manage the state of KubeVirt VirtualMachines.

version_added: "2.5"

author: KubeVirt Team (@kubevirt)

options:
    state:
        description:
            - Set the VirtualMachine to either (C(running)) or (C(stopped)).
        required: false
        default: "running"
        choices:
            - running
            - stopped
        type: str
    name:
        description:
            - Name of the VirtualMachine.
        required: true
        type: str
    namespace:
        description:
            - Namespace where the VirtualMachine exists.
        required: true
        type: str
    api_version:
        description:
            - KubeVirt API version to use.
        required: false
        type: str
        default: v1alpha2
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
        type: bool
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
    - kubernetes python client >= 6.0.0
'''

EXAMPLES = '''
- name: Set baldr VM running
  kubevirt_vm_status:
      state: running
      name: baldr
      namespace: vms
'''

RETURN = '''
result:
    description:
        - When replica number is different, otherwise empty.
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
                          on the I(api_version)."
            returned: success
            type: complex
        status:
            description: Current status details for the resource.
            returned: success
            type: complex
'''

import copy
import os
import sys
import kubernetes.client
from ansible.module_utils.six import iteritems

if hasattr(sys, '_called_from_test'):
    sys.path.append('lib/ansible/module_utils/k8svirt')
    from helper import NAME_ARG_SPEC, AUTH_ARG_SPEC
    from common import K8sVirtAnsibleModule
else:
    from ansible.module_utils.k8svirt.helper import NAME_ARG_SPEC, \
        AUTH_ARG_SPEC
    from ansible.module_utils.k8svirt.common import K8sVirtAnsibleModule

from kubernetes.client.rest import ApiException
from kubernetes.config import kube_config, ConfigException


class KubeVirtVMStatus(K8sVirtAnsibleModule):
    def __init__(self, *args, **kwargs):
        super(KubeVirtVMStatus, self).__init__(*args, **kwargs)
        self._api_client = None

    @property
    def argspec(self):
        """ argspec property builder """
        argspec = copy.deepcopy(NAME_ARG_SPEC)
        argspec.update(copy.deepcopy(AUTH_ARG_SPEC))
        argspec['name']['required'] = True
        argspec['namespace']['required'] = True
        argspec['api_version']['default'] = 'v1alpha2'
        argspec['state'] = dict({
            'required': False, 'type': 'str',
            'choices': list(['running', 'stopped']), 'default': 'running'
        })
        return argspec

    def execute_module(self):
        """ Module execution """
        api_client = self.__authenticate()
        api_instance = kubernetes.client.CustomObjectsApi(
            api_client=api_client)
        group = 'kubevirt.io'
        plural = 'virtualmachines'
        version = self.params.get('api_version')
        namespace = self.params.get('namespace')
        name = self.params.get('name')
        state = True if self.params.get('state') == 'running' else False
        body = dict()
        body['spec'] = dict({'running': state})

        try:
            exists = api_instance.get_namespaced_custom_object(
                group, version, namespace, plural, name)
            current_state = exists.get('spec').get('running')

            if current_state == state:
                self.exit_json(changed=False)

            api_response = api_instance.patch_namespaced_custom_object(
                group, version, namespace, plural, name, body)
            self.exit_json(changed=True, result=api_response)
        except ApiException as exc:
            self.fail_json(msg='Failed to manage requested object',
                           error=exc.reason)

    def __authenticate(self):
        """ Build API client based on user's configuration """
        host = self.params.get('host')
        username = self.params.get('username')
        password = self.params.get('password')
        api_key = self.params.get('api_key')

        if (host and username and password) or (api_key and host):
            return self.__configure_by_params()
        return self.__configure_by_file()

    def __configure_by_file(self):
        """ Return API client from configuration file """
        if not self.params.get('kubeconfig'):
            config_file = os.path.expanduser(
                kube_config.KUBE_CONFIG_DEFAULT_LOCATION)
        else:
            config_file = self.params.get('kubeconfig')

        try:
            kube_config.load_kube_config(
                config_file=config_file,
                context=self.params.get('context')
            )
            config = kubernetes.client.Configuration()
            if not self.params.get('verify_ssl'):
                setattr(config, 'verify_ssl', False)
            return kubernetes.client.ApiClient(
                configuration=config
            )
        except (IOError, ConfigException):
            raise

    def __configure_by_params(self):
        """ Return API client from configuration file """
        kube_config.load_kube_config()
        config = kubernetes.client.Configuration()
        auth_args = AUTH_ARG_SPEC.keys()

        for key, value in iteritems(self.params):
            if key in auth_args and value is not None:
                if key == 'api_key':
                    setattr(
                        config,
                        key, {'authorization': "Bearer {0}".format(value)})
                else:
                    setattr(config, key, value)

        if not self.params.get('verify_ssl'):
            setattr(config, 'verify_ssl', False)

        return kubernetes.client.ApiClient(configuration=config)


if __name__ == '__main__':
    KubeVirtVMStatus().execute_module()
