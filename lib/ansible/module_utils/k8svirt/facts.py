#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0
# (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

import copy
import sys

from kubevirt.rest import ApiException
# TODO: This is ugly, either find a way to make it always work or clean it up
# before sending PR to Ansible
if hasattr(sys, '_called_from_test'):
    sys.path.append('lib/ansible/module_utils/k8svirt')
    from common import K8sVirtAnsibleModule
    from helper import AUTH_ARG_SPEC, NAME_ARG_SPEC, FACTS_ARG_SPEC, \
        get_helper, to_snake
else:
    from ansible.module_utils.k8svirt.helper import get_helper, AUTH_ARG_SPEC,\
        NAME_ARG_SPEC, FACTS_ARG_SPEC, to_snake
    from ansible.module_utils.k8svirt.common import K8sVirtAnsibleModule


class KubeVirtFacts(K8sVirtAnsibleModule):
    """ KubeVirtFacts common class """
    def __init__(self, *args, **kwargs):
        """ Class constructor """
        self._api_client = None
        self._core_api_client = None
        self._kubevirt_obj = None
        super(KubeVirtFacts, self).__init__(*args, **kwargs)

    @property
    def argspec(self):
        """ Merge the initial module arguments """
        argspec = copy.deepcopy(FACTS_ARG_SPEC)
        argspec.update(copy.deepcopy(NAME_ARG_SPEC))
        argspec.update(copy.deepcopy(AUTH_ARG_SPEC))
        return argspec

    def execute_module(self):
        """ Gather the actual facts """
        self._api_client, self._core_api_client = self.authenticate()
        kind = to_snake(self.params.get('kind'))
        res_helper = get_helper(self._api_client, self._core_api_client, kind)
        try:
            self._kubevirt_obj = res_helper.list(
                namespace=self.params.get('namespace'),
                name=self.params.get('name'),
                field_selectors=self.params['field_selectors'],
                label_selectors=self.params['label_selectors']
            )
            self._kubevirt_obj = copy.deepcopy(self.__resource_cleanup())
            return self._kubevirt_obj
        except ApiException as exc:
            self.fail_json(msg='Failed to retrieve requested object',
                           error=str(exc))

    def __resource_cleanup(self, subdict=None):
        """ Cleanup null keys """
        if subdict is None:
            subdict = self._kubevirt_obj.to_dict()
        for key, value in subdict.items():
            if value is None or value == '':
                del subdict[key]
            elif isinstance(value, dict):
                self.__resource_cleanup(value)
            elif isinstance(value, list):
                subdict[key] = self.__list_cleanup(value)
        return subdict

    def __list_cleanup(self, value):
        """ Cleanup list items """
        aux = list()
        for i in value:
            if isinstance(i, dict):
                aux.append(self.__resource_cleanup(i))
            else:
                aux.append(i)
        return aux
