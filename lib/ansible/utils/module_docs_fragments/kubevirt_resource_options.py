# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0
# (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)


class ModuleDocFragment(object):
    DOCUMENTATION = '''
options:
  state:
    description:
    - "Determine if an object should be created, patched, or deleted.
      When set to C(present), an object will be created,
      if it does not already exist. If set to C(absent), an existing
      object will be deleted."
  force:
    description:
    - "If set to C(yes) and state is C(present) to force update KubeVirt
      resources."
  resource_definition:
    description:
    - Provide a valid YAML definition for an object when creating or updating.
  src:
    description:
    - "Provide a path to a file containing a valid YAML definition of an object
      or objects to be created or updated. Mutually exclusive
      with I(resource_definition)."
'''
