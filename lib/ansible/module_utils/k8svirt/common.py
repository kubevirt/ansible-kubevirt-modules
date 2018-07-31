#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0
# (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

import os
import sys
import yaml
import kubevirt as sdk

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems
if hasattr(sys, '_called_from_test'):
    sys.path.append('lib/ansible/module_utils/k8svirt')
    from helper import AUTH_ARG_SPEC
else:
    from ansible.module_utils.k8svirt.helper import AUTH_ARG_SPEC

from kubernetes.config import kube_config, ConfigException


class K8sVirtAnsibleModule(AnsibleModule):
    """ Module utils for KubeVirt Ansible modules """
    def __init__(self, *args, **kwargs):
        """ Class constructor """
        kwargs['argument_spec'] = self.argspec
        super(K8sVirtAnsibleModule, self).__init__(*args, **kwargs)

    @property
    def argspec(self):
        """ arg_spec builder to be implemented on each subclass """
        raise NotImplementedError()

    def execute_module(self):
        """ Module execution to be implemented on each subclass """
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
            if not self.params.get('verify_ssl'):
                sdk.configuration.verify_ssl = False
            kube_config.load_kube_config(
                config_file=config_file,
                context=self.params.get('context'),
                client_configuration=sdk.configuration
            )
            return sdk.DefaultApi()
        except (IOError, ConfigException):
            raise

    def __configure_by_params(self):
        """ Return API client from configuration file """
        auth_args = AUTH_ARG_SPEC.keys()

        for key, value in iteritems(self.params):
            if key in auth_args and value is not None:
                if key == 'api_key':
                    setattr(
                        sdk.configuration,
                        key, {'authorization': "Bearer {0}".format(value)})
                else:
                    setattr(sdk.configuration, key, value)

        if not self.params.get('verify_ssl'):
            sdk.configuration.verify_ssl = False

        kube_config.load_kube_config(client_configuration=sdk.configuration)

        return sdk.DefaultApi()
