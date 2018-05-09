# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0
# (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

import os
import copy
from kubernetes.config import kube_config
import kubevirt as sdk

from ansible.module_utils.kubevirt.common import KubeVirtAnsibleModule
from ansible.module_utils.kubevirt.helper import to_snake, COMMON_ARG_SPEC
from kubevirt.rest import ApiException as KubeVirtApiException
from kubevirt.apis import DefaultApi as KubeVirtDefaultApi


class KubeVirtRawModule(KubeVirtAnsibleModule):
    """ # """
    def __init__(self, *args, **kwargs):
        """ Class constructor """
        mutually_exclusive = [
            ('resource_definition', 'src')
        ]

        KubeVirtAnsibleModule.___init__(self, *args,
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

        self.api_version = self.api_version.lower()
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
        return argspec

    def execute_module(self):
        """ Method for handling module's actions """

        if self.resource_definition:
            resource_params = self.resource_to_parameters(
                self.resource_definition)
            self.params.update(resource_params)

        state = self.params.get('state')
        self._authenticate()
        existing = self._get_object()

        if state == 'present':
            if existing:
                # resource already exists
                self.exit_json(changed=False, result=dict())
            else:
                self._create()

    def _get_object(self):
        kubevirt_obj = None
        try:
            kubevirt_obj = self._api_client.read_namespaced_virtual_machine(
                self.params.get('name'), self.params.get('namespace'),
                export=True
            )
        except KubeVirtApiException as exc:
            self.fail_json(msg='Failed to retrieve requested object',
                           error=exc.value.get('status'))
        return kubevirt_obj

    def _authenticate(self):
        if os.path.exists(
                os.path.expanduser(kube_config.KUBE_CONFIG_DEFAULT_LOCATION)):
            kube_config.load_kube_config(
                client_configuration=sdk.configuration)
            self._api_client = KubeVirtDefaultApi()

    def _create(self):
        try:
            body = sdk.V1VirtualMachine()
            body.update(copy.deepcopy(self.resource_definition))
            self._api_client.create_namespaced_virtual_machine(
                body, self.params.get('namespace')
            )
        except KubeVirtApiException as exc:
            self.fail_json(msg='Failed to create requested resource',
                           error=exc.value.get('status'))
