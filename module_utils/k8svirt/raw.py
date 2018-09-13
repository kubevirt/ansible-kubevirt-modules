# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0
# (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

import copy
import sys

# TODO: This is ugly, either find a way to make it always work or clean it up
# before sending PR to Ansible
if hasattr(sys, '_called_from_test'):
    sys.path.append('module_utils/k8svirt')
    from common import K8sVirtAnsibleModule
    from helper import to_snake, NAME_ARG_SPEC, RESOURCE_ARG_SPEC, \
        STATE_ARG_SPEC, AUTH_ARG_SPEC, get_helper
else:
    from ansible.module_utils.k8svirt.common import K8sVirtAnsibleModule
    from ansible.module_utils.k8svirt.helper import to_snake, NAME_ARG_SPEC,\
        RESOURCE_ARG_SPEC, STATE_ARG_SPEC, AUTH_ARG_SPEC, get_helper


from kubevirt.rest import ApiException as KubeVirtApiException
from kubernetes.client.rest import ApiException as CoreApiException


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
        self._core_api_client = None
        self._helper = None
        self.kind = self.params.pop('kind')
        self.api_version = self.params.pop('api_version')
        self.resource_definition = self.params.pop('resource_definition')
        self.src = self.params.pop('src')
        if self.src:
            self.resource_definition = self.load_resource_definition(self.src)

        if self.resource_definition:
            if not self.api_version:
                self.api_version = self.resource_definition.get('apiVersion')
            if not self.kind:
                self.kind = self.resource_definition.get('kind')

    @property
    def argspec(self):
        """ Merge the initial module arguments """
        argspec = copy.deepcopy(NAME_ARG_SPEC)
        argspec.update(copy.deepcopy(AUTH_ARG_SPEC))
        argspec.update(copy.deepcopy(RESOURCE_ARG_SPEC))
        argspec.update(copy.deepcopy(STATE_ARG_SPEC))
        return argspec

    def execute_module(self):
        """ Method for handling module's actions """
        if not self.api_version:
            self.fail_json(
                msg=("Error: missing api_version. Use the api_version ",
                     "parameter of specify it as part of a ",
                     "resource_definition.")
            )
        elif not self.kind:
            self.fail_json(
                msg=("Error: missing kind. Use the kind parameter ",
                     "or specify it as part of a resource_definition."))
        else:
            self.api_version = str(self.api_version).lower()
            self.kind = to_snake(self.kind)
            state = self.params.get('state')
            self.wait = self.params.pop('wait')
            self.timeout = self.params.pop('timeout')
            self._api_client, self._core_api_client = self.authenticate()
            self._helper = get_helper(
                self._api_client, self._core_api_client, self.kind)
            existing = self.__get_object()

            if state == 'present':
                if existing and self.params.get('force'):
                    meta = self.__replace()
                    self.exit_json(changed=True, result=dict(meta.to_dict()))
                elif existing:
                    self.exit_json(changed=False, result=dict())
                else:
                    meta = self.__create()
                    self.exit_json(changed=True, result=dict(meta.to_dict()))
            elif state == 'absent':
                if existing:
                    self.__delete()
                    self.exit_json(changed=True, result=dict())
                else:
                    self.exit_json(changed=False, result=dict())

    def __get_object(self):
        kubevirt_obj = None
        try:
            kubevirt_obj = self._helper.exists(
                self.params.get('name'), self.params.get('namespace')
            )
            return kubevirt_obj
        except (KubeVirtApiException, CoreApiException) as exc:
            if exc.status != 404:
                self.fail_json(msg='Failed to retrieve requested object',
                               error=exc.reason)

    def __create(self):
        try:
            return self._helper.create(
                self.resource_definition, self.params.get('namespace'),
                self.wait, self.timeout)
        except KubeVirtApiException as exc:
            self.fail_json(msg='Failed to create requested resource',
                           error=exc.reason)

    def __replace(self):
        try:
            return self._helper.replace(
                self.resource_definition, self.params.get('namespace'),
                self.params.get('name'))
        except KubeVirtApiException as exc:
            self.fail_json(msg='Failed to replace requested resource',
                           error=exc.reason)

    def __delete(self):
        try:
            self._helper.delete(
                self.params.get('name'), self.params.get('namespace'))
        except KubeVirtApiException as exc:
            self.fail_json(msg='Failed to delete requested resource',
                           error=exc.reason)
