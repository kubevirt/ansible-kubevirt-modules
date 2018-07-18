# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0
# (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)


class ModuleDocFragment(object):
    DOCUMENTATION = '''
options:
  kubeconfig:
    description:
    - "Path to an existing Kubernetes config file. If not provided,
       and no other connection options are provided, the kubernetes
       client will attempt to load the default configuration file
       from I(~/.kube/config.json)."
  context:
    description:
    - The name of a context found in the config file.
  host:
    description:
    - Provide a URL for accessing the API.
  api_key:
    description:
    - Token used to authenticate with the API.
  username:
    description:
    - Provide a username for authenticating with the API.
  password:
    description:
    - Provide a password for authenticating with the API.
  verify_ssl:
    description:
    - Whether or not to verify the API server's SSL certificates.
  ssl_ca_cert:
    description:
    - Path to a CA certificate used to authenticate with the API.
  cert_file:
    description:
    - Path to a certificate used to authenticate with the API.
  key_file:
    description:
    - Path to a key file used to authenticate with the API.
'''
