#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0
# (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

import os
import yaml
import kubevirt as sdk

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems
from kubevirt import DefaultApi as KubeVirtDefaultApi
from kubernetes.config import kube_config


class K8sVirtAnsibleModule(AnsibleModule):
    """ Module utils for KubeVirt Ansible modules """
    def __init__(self, *args, **kwargs):
        """ Class constructor """
        kwargs['argument_spec'] = self.argspec
        super(K8sVirtAnsibleModule, self).__init__(*args, **kwargs)

    @property
    def argspec(self):
        raise NotImplementedError()

    def execute_module(self):
        raise NotImplementedError()

    def load_resource_definition(self, src):
        """ Load the requested src path """
        result = None
        path = os.path.normpath(src)
        if not os.path.exists(path):
            self.fail_json(
                msg="Error accessing {0}. Does the file exist?".format(path))
        try:
            result = yaml.safe_load(open(path, 'r'))
        except (IOError, yaml.YAMLError) as exc:
            self.fail_json(
                msg="Error loading resource_definition: {0}".format(exc))
        return result

    def authenticate(self):
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
            return KubeVirtDefaultApi()
