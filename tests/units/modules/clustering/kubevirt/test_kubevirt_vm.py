import json
import sys

# FIXME: paths/imports should be fixed before submitting a PR to Ansible
sys.path.append('lib/ansible/modules/clustering/kubevirt')

import kubevirt_vm as mymodule


class TestKubeVirtVmModule(object):

    def test_simple_merge_dicts(self):
        dict1 = {'labels': {'label1': 'value'}}
        dict2 = {'labels': {'label2': 'value'}}
        dict3 = json.dumps({'labels': {'label1': 'value', 'label2': 'value'}}, sort_keys=True)
        assert dict3 == json.dumps(dict(mymodule.KubeVirtVM.merge_dicts(dict1, dict2)))

    def test_simple_multi_merge_dicts(self):
        dict1 = {'labels': {'label1': 'value', 'label3': 'value'}}
        dict2 = {'labels': {'label2': 'value'}}
        dict3 = json.dumps({'labels': {'label1': 'value', 'label2': 'value', 'label3': 'value'}}, sort_keys=True)
        assert dict3 == json.dumps(dict(mymodule.KubeVirtVM.merge_dicts(dict1, dict2)))

    def test_double_nested_merge_dicts(self):
        dict1 = {'metadata': {'labels': {'label1': 'value', 'label3': 'value'}}}
        dict2 = {'metadata': {'labels': {'label2': 'value'}}}
        dict3 = json.dumps({'metadata': {'labels': {'label1': 'value', 'label2': 'value', 'label3': 'value'}}}, sort_keys=True)
        assert dict3 == json.dumps(dict(mymodule.KubeVirtVM.merge_dicts(dict1, dict2)))
