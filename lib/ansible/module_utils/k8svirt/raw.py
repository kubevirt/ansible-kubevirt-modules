# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0
# (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

import os
import copy
import sys
import kubevirt as sdk

from ansible.module_utils.six import iteritems

# TODO: This is ugly, either find a way to make it always work or clean it up
# before sending PR to Ansible
if hasattr(sys, '_called_from_test'):
    sys.path.append('lib/ansible/module_utils/k8svirt')
    from common import K8sVirtAnsibleModule
    from helper import to_snake, COMMON_ARG_SPEC, \
        AUTH_ARG_SPEC, get_helper
else:
    from ansible.module_utils.k8svirt.common import K8sVirtAnsibleModule
    from ansible.module_utils.k8svirt.helper import to_snake, COMMON_ARG_SPEC,\
        AUTH_ARG_SPEC, get_helper


from kubernetes.config import kube_config
from kubevirt import DefaultApi as KubeVirtDefaultApi
from kubevirt.rest import ApiException as KubeVirtApiException


class KubeVirtRawModule(K8sVirtAnsibleModule):
    """ # """
    def __init__(self, *args, **kwargs):
        """ Class constructor """
        mutually_exclusive = [
            ('resource_definition', 'src')
        ]

        super(KubeVirtRawModule, self).__init__(
            *args,
            mutually_exclusive=mutually_exclusive,
            supports_check_mode=False,
            **kwargs)

        self._api_client = None
        self.kind = self.params.pop('kind')
        self.api_version = self.params.pop('api_version')
        self.resource_definition = self.params.pop('resource_definition')
        self.src = self.params.pop('src')
        if self.src:
            self.resource_definition = self.load_resource_definition(self.src)

        if self.resource_definition:
            self.api_version = self.resource_definition.get('apiVersion')
            self.kind = self.resource_definition.get('kind')

        self.api_version = str(self.api_version).lower()
        self.kind = to_snake(self.kind)

        if not self.api_version:
            self.fail_json(
                msg=("Error: missing api_version. Use the api_version ",
                     "parameter of specify it as part of a ",
                     "resource_definition.")
            )

        if not self.kind:
            self.fail_json(
                msg=("Error: missing kind. Use the kind parameter ",
                     "or specify it as part of a resource_definition.")
            )

    @property
    def argspec(self):
        """ Merge the initial module arguments """
        argspec = copy.deepcopy(COMMON_ARG_SPEC)
        argspec.update(copy.deepcopy(AUTH_ARG_SPEC))
        return argspec

    def execute_module(self):
        """ Method for handling module's actions """
        state = self.params.get('state')
        self.__authenticate()
        existing = self.__get_object()

        if state == 'present':
            if existing:
                self.exit_json(changed=False, result=dict())
            else:
                self.__create()
                self.exit_json(changed=True, result=dict())
        elif state == 'absent':
            if existing:
                self.__delete()
                self.exit_json(changed=True, result=dict())
            else:
                self.exit_json(changed=False, result=dict())

    def __get_object(self):
        kubevirt_obj = None
        helper = get_helper(self._api_client, self.kind)
        try:
            kubevirt_obj = helper.exists(
                self.params.get('name'), self.params.get('namespace')
            )
        except KubeVirtApiException as exc:
            if exc.status != 404:
                self.fail_json(msg='Failed to retrieve requested object',
                               error=exc.reason)
        return kubevirt_obj

    def __authenticate(self):
        auth_options = {}
        # FIXME: removed kubeconfig, context
        auth_args = ('host', 'api_key', 'username', 'password', 'cert_file',
                     'key_file', 'ssl_ca_cert', 'verify_ssl')
        for key, value in iteritems(self.params):
            if key in auth_args and value is not None:
                auth_options[key] = value

        if os.path.exists(
                os.path.expanduser(kube_config.KUBE_CONFIG_DEFAULT_LOCATION)):
            if not self.params.get('verify_ssl'):
                sdk.configuration.verify_ssl = False
            kube_config.load_kube_config(
                client_configuration=sdk.configuration)
            self._api_client = KubeVirtDefaultApi()

    def __create(self):
        try:
            helper = get_helper(self._api_client, self.kind)
            helper.create(
                self.resource_definition, self.params.get('namespace'))
        except KubeVirtApiException as exc:
            self.fail_json(msg='Failed to create requested resource',
                           error=exc.reason)

    def __delete(self):
        try:
            helper = get_helper(self._api_client, self.kind)
            helper.delete(
                self.params.get('name'), self.params.get('namespace'))
        except KubeVirtApiException as exc:
            self.fail_json(msg='Failed to delete requested resource',
                           error=exc.reason)
