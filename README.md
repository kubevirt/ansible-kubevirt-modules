# Ansible KubeVirt Modules

[Ansible](https://github.com/ansible/ansible) modules for [KubeVirt](https://github.com/kubevirt/kubevirt) management.

## Contents

- `lib`: Ansible modules files for KubeVirt management
    - `kubevirt_raw`: Allow to manage KubeVirt resources, VirtualMachineInstance, VirtualMachine, VirtualMachineInstanceReplicaSet and VirtualMachineInstancePresets.
    - `kubevirt_facts`: Gather facts about a given resource.
    - `kubevirt_vm_status`: Set an VirtualMachine to either `running` or `stopped`.
    - `kubevirt_scale_vmirs`: Scale up or down a VirtualMachineInstanceReplilcaSet.
- `tests`: Ansible playbook examples and unit tests

## Requirements

- Ansible >= 2.4.3.0
- [KubeVirt Python SDK](https://github.com/kubevirt/client-python)
- [Kubernetes Python client](https://github.com/kubernetes-client/python)
- [KubeVirt](https://github.com/kubevirt/kubevirt)

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

4. [Install KubeVirt Python SDK](https://github.com/kubevirt/client-python#installation--usage)

5. [Install Kubernetes Python client](https://github.com/kubernetes-client/python/#installation)

6. Once installed, add it to a playbook:

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

* [Virtual Machine Instance](tests/playbooks/kubevirt_raw_vmi.yml)
* [Virtual Machine](tests/playbooks/kubevirt_raw_vm.yml)
* [Virtual Machine Instance ReplicaSet](tests/playbooks/kubevirt_raw_vmirs.yml)
* [Stop Virtual Machine](tests/playbooks/kubevirt_vm_stopped.yml)
* [Scale Virtual Machine Instance Replica Set](tests/playbooks/kubevirt_scale_vmirs.yml)
* [Virtual Machine Instance facts](tests/playbooks/kubevirt_vmi_facts.yml)
* [Virtual Machine facts](tests/playbooks/kubevirt_vm_facts.yml)
* [Virtual Machine Instance ReplicaSet facts](tests/playbooks/kubevirt_vmirs_facts.yml)
* [All Virtual Machine Instance facts](tests/playbooks/kubevirt_all_vmis_facts.yml)

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
        
        $ ssh -i tests/kubevirt_rsa -p 27017 kubevirt@172.30.133.9
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
$ ansible-playbook tests/playbooks/kubevirt_vm_facts.yml
```

The above command, will gather the information for the VM stated in the playbook and print out a JSON document based on [KubeVirt VM spec](https://kubevirt.io/api-reference/master/definitions.html#_v1_virtualmachine).
