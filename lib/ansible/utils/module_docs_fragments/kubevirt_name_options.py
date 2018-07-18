# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0
# (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)


class ModuleDocFragment(object):
    DOCUMENTATION = '''
options:
  name:
    description:
    - "Use to specify an object name. Use to create, delete, or discover
       an object without providing a full resource definition."
  namespace:
    description:
    - "Use to specify an object namespace. Useful when creating, deleting,
       or discovering an object without providing a full resource definition."
  kind:
    description:
    - "Use to specify an object model. Use to create, delete, or discover
       an object without providing a full resource definition."
  api_version:
    description:
    - "Use to specify the API version. Use to create, delete, or discover
       an object without providing a full resource definition."
'''
