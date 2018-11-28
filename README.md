# Ansible KubeVirt Modules

[Ansible](https://github.com/ansible/ansible) modules for [KubeVirt](https://github.com/kubevirt/kubevirt) management.

## Contents

- `lib`: Ansible modules files for KubeVirt management
    - `kubevirt_vm`: Manage virtual machines
    - `kubevirt_scale_vmirs`: Scale up or down a VirtualMachineInstanceReplilcaSet.
- `tests`: Ansible playbook examples and unit tests

## Requirements

- Ansible >= 2.7
- [OpenShift Python client](https://github.com/openshift/openshift-restclient-python)

## Installation and usage

1. Install the modules:
    1. From GitHub:

        ```shell
        $ git clone https://github.com/kubevirt/ansible-kubevirt-modules
        ```

    2. From [Ansible Galaxy](https://galaxy.ansible.com/kubevirt/kubevirt-modules/)

        ```shell
        $ ansible-galaxy install -p <roles_path> kubevirt.kubevirt-modules
        ```

2. Setting up the environment

```shell
$ export ANSIBLE_MODULE_UTILS=<module_path>/lib/ansible/module_utils
$ export ANSIBLE_LIBRARY=<module_path>/lib/ansible/modules
```

> **NOTE:** These settings can instead be added to *ansible.cfg* as done in [test/ansible.cfg](tests/ansible.cfg)

3. A working [Kubernetes configuration](https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/) is also required. It can also be created by issuing `oc login` if using KubeVirt with OpenShift.

4. [Install OpenShift Python SDK](https://github.com/openshift/openshift-restclient-python#installation)

5. Once installed, add it to a playbook:

```yaml
---
- hosts: localhost
  roles:
    - role: ansible-kubevirt-modules
      install_python_requirements: no
    - role: hello-underworld
```

Because the role is referenced, the `hello-underworld` role is able to make use of the kubevirt modules.

## Playbook examples

* [Virtual Machine Instance](tests/playbooks/k8s_vmi.yml)
* [Virtual Machine](tests/playbooks/k8s_vm.yml)
* [Virtual Machine Instance ReplicaSet](tests/playbooks/k8s_vmirs.yml)
* [Stop Virtual Machine](tests/playbooks/kubevirt_vm_status.yml)
* [Scale Virtual Machine Instance Replica Set](tests/playbooks/kubevirt_scale_vmirs.yml)
* [Virtual Machine Instance facts](tests/playbooks/k8s_facts_vmi.yml)
* [Virtual Machine facts](tests/playbooks/k8s_facts_vm.yml)
* [Virtual Machine Instance ReplicaSet facts](tests/playbooks/k8s_facts_vmirs.yml)
* [All Virtual Machine Instance facts](tests/playbooks/k8s_facts.yml)

## Local testing

1. Run the tests as follows:

```shell
$ export ANSIBLE_CONFIG=tests/ansible.cfg
$ ansible-playbook tests/playbooks/<playbook>
```
> If your cluser has a self-signed certificate, you can include `verify_ssl = false` in `tests/ansible.cfg`

2. The playbook examples, include [cloud-init](http://cloudinit.readthedocs.io/en/latest/) configuration, for being able to access the VMIs created.

    1. For using SSH do as follows:

        ```shell
        $ kubectl get all
        NAME                             READY     STATUS    RESTARTS   AGE
        po/virt-launcher-bbecker-jw5kk   1/1       Running   0          22m

        $ kubectl expose pod virt-launcher-bbecker-jw5kk --port=27017 --target-port=22 --name=vmservice
        $ kubectl get svc vmservice
        NAME        TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)     AGE
        vmservice   ClusterIP   172.30.133.9   <none>        27017/TCP   19m

        $ ssh -i tests/test_rsa -p 27017 kubevirt@172.30.133.9
        ```

        > **NOTE:** It might take a while for the VM to completely come up before SSH can be used.

    2. For using `virtctl`:

        ```shell
        $ virtctl console <vmi_name>
        ```

        Or

        ```shell
        $ virtctl vnc <vmi_name>
        ```

        > **NOTE:** Use username `kubevirt` and password `kubevirt`.


### Facts

* Once one of the previous resources has been created, the facts module can be tested as well as follows:

```shell
$ ansible-playbook tests/playbooks/k8s_facts_vm.yml
```

The above command, will gather the information for the VM stated in the playbook and print out a JSON document based on [KubeVirt VM spec](https://kubevirt.io/api-reference/master/definitions.html#_v1_virtualmachine).
