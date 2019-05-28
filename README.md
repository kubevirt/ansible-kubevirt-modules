# Ansible KubeVirt Modules

KubeVirt Ansible modules enable you to automate cluster management tasks such as template, persistent volume claim, and virtual machine management.

For the source code of KubeVirt modules see the [Ansible repository](https://github.com/ansible/ansible/tree/devel/lib/ansible/modules/cloud/kubevirt). This repo contains only the integration tests for these modules.

## Requirements

* Ansible >= 2.8
* OpenShift >= 0.8.2


## Integration tests

* [Virtual Machine Instance](tests/playbooks/k8s_vmi.yml)
* [Virtual Machine](tests/playbooks/k8s_vm.yml)
* [Virtual Machine Instance ReplicaSet](tests/playbooks/k8s_vmirs.yml)
* [Stop Virtual Machine](tests/playbooks/kubevirt_vm_status.yml)
* [Scale Virtual Machine Instance Replica Set](tests/playbooks/kubevirt_scale_vmirs.yml)
* [Virtual Machine Instance facts](tests/playbooks/k8s_facts_vmi.yml)
* [Virtual Machine facts](tests/playbooks/k8s_facts_vm.yml)
* [Virtual Machine Instance ReplicaSet facts](tests/playbooks/k8s_facts_vmirs.yml)
* [All Virtual Machine Instance facts](tests/playbooks/k8s_facts.yml)

For the full list see [tests/playbooks](./tests/playbooks).

## How to run the tests?

1. Clone this repository to the machine, where you can run `oc login` to your cluster:

```shell
$ git clone https://github.com/kubevirt/ansible-kubevirt-modules.git
$ cd ./ansible-kubevirt-modules
```

2. (Optional) Configure a virtual environment to isolate dependencies:

```shell
$ python3 -m venv env
$ source env/bin/activate
```

3. Install dependencies:

```shell
$ pip install openshift
```

To install Ansible use one of the options below:

    * Install the [latest release version](https://github.com/ansible/ansible/releases):
    
    ```shell
    $ pip install ansible
    ```
    
    * Build RPM from the devel branch:
    
    ```shell
    $ git clone https://github.com/ansible/ansible.git
    $ cd ./ansible
    $ make rpm
    $ sudo rpm -Uvh ./rpm-build/ansible-*.noarch.rpm
    ```
    
    * [Check out PRs locally](https://help.github.com/en/articles/checking-out-pull-requests-locally)
    

4. Run the tests:

```shell
$ export ANSIBLE_CONFIG=tests/ansible.cfg
$ ansible-playbook tests/playbooks/<playbook>
```
>**Note**: If your cluser has a self-signed certificate, you can include `verify_ssl = false` in `tests/ansible.cfg`

>**Note**: The playbook examples include [cloud-init](http://cloudinit.readthedocs.io/en/latest/) configuration to be able to access the created VMIs.

    i. For using SSH do as follows:

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

        It might take a while for the VM to come up before SSH can be used.

    ii. For using `virtctl`:

        ```shell
        $ virtctl console <vmi_name>
        ```

        Or

        ```shell
        $ virtctl vnc <vmi_name>
        ```

        Use the username `kubevirt` and the password `kubevirt`.

5. (Optional) Leave the virtual environment and remove it:

```shell
$ deactivate
$ rm -rf env/
```


### Using the `kubevirt_cdi_upload` module

To upload an image from localhost by using the `kubevirt_cdi_upload` module, your system needs to be able to connect to the [cdi upload proxy pod](https://github.com/kubevirt/containerized-data-importer/blob/master/doc/upload.md). This can be achieved by either:

1. Exposing the `cdi-uploadproxy` Service from the `cdi` namespace, or

2. Using `kubectl port-forward` to set up a temporary port forwarding through the Kubernetes API server: `kubectl port-forward -n cdi service/cdi-uploadproxy 9443:443`

### Using the `Facts` module

The following command will collect facts about the existing VM(s), if there are any, and print out a JSON document based on [KubeVirt VM spec](https://kubevirt.io/api-reference/master/definitions.html#_v1_virtualmachine):

```shell
$ ansible-playbook tests/playbooks/k8s_facts_vm.yml
```

## KubeVirt Inventory plugin
Inventory plugins allow users to point at data sources to compile the inventory of hosts that Ansible uses to target tasks, either via the `-i /path/to/file` and/or `-i 'host1, host2'` command line parameters or from other configuration sources.

### Enabling the KubeVirt inventory plugin
To enable the KubeVirt plugin, add the following section in the `tests/ansible.cfg` file:

```
[inventory]
enable_plugins = kubevirt
```

### Configuring the KubeVirt inventory plugin
Define the plugin configuration in `tests/playbooks/plugin/kubevirt.yaml` as follows:

```
plugin: kubevirt
connections:
  - namespaces:
      - default
    interface_name: default
```

In this example, the KubeVirt plugin will list all VMIs from the `default` namespace and use the `default` interface name.

### Using the KubeVirt inventory plugin
To use the plugin in a playbook, run:

```
$ ansible-playbook -i kubevirt.yaml <playbook>
```

>**Note**: The KubeVirt inventory plugin is designed to work with Multus. It can be used only for VMIs, which are connected to the bridge and display the IP address in the Status field. For VMIs exposed by Kubernetes services, please use the [k8s Ansible module](https://docs.ansible.com/ansible/latest/plugins/inventory/k8s.html).

## Automatic testing

### Unit tests

Upstream [ansible](https://github.com/ansible/ansible) repository contains unit tests covering the kubevirt modules.

### Integration tests

Module and role tests ([tests/playbooks/all.yml](tests/playbooks/all.yml) and [tests/roles/deploy.yml](tests/roles/deploy.yml) respectively) are run
against actual clusters with both [KubeVirt](https://github.com/kubevirt/kubevirt) and [CDI](https://github.com/kubevirt/containerized-data-importer) deployed, on top of:
- TravisCI (ubuntu vms supporting only minikube; no kvm acceleration for KubeVirt vms)
- oVirt Jenkins (physical servers that run any cluster [kubevirtci](https://github.com/kubevirt/kubevirtci) supports)

Module tests are run using:
- most recently released ansible (whatever one gets with `pip install ansible`)
- ansible stable branch(es)
- ansible devel branch

To detect regressions early, Travis runs all the tests every 24 hours against a fresh clone of ansible.git and emails kubevirt module developers if tests fail.
