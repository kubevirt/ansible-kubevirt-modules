# This collection is obsolete and has been replaced by the [kubevirt.core](https://github.com/kubevirt/kubevirt.core) Ansible collection.

# Ansible KubeVirt Modules

Ansible KubeVirt modules enable the automation of management of the following Kubernetes cluster object types:
* Virtual Machines (also VM templates and VM presets),
* VM Replica Sets,
* and Persistent Volume Claims (including [Containerized Data Importer][cdi.git] functionality).

Since the release of Ansible 2.8, the modules, the inventory plugin and relevant unit tests are part of the
[upstream Ansible git repository][ansible.git], while this repository contains only the integration tests
and example playbooks.

[cdi.git]: https://github.com/kubevirt/containerized-data-importer
[ansible.git]: https://github.com/ansible/ansible
[kubevirt.git]: https://github.com/kubevirt/kubevirt
[kubevirtci.git]: https://github.com/kubevirt/kubevirtci
[kubevirt.io]: https://kubevirt.io/
[openshift-restclient-python.git]: https://github.com/openshift/openshift-restclient-python


### Table of Contents

* **[Quickstart](#quickstart)**
* **[Requirements](#requirements)**
* **[Source Code](#source-code)**
* **[Testing](#testing)**
  * **[Automatic testing](#automatic-testing)**
  * **[Manual testing](#manual-testing)**


## Quickstart

For a quick introduction, please see the following [kubevirt.io][kubevirt.io] blog posts:
* [KubeVirt with Ansible, part 1 – Introduction](https://kubevirt.io/2019/kubevirt-with-ansible-part-1.html)
* [KubeVirt with Ansible, part 2](https://kubevirt.io/2019/kubevirt-with-ansible-part-2.html)


## Requirements

* Ansible >= 2.8
  * `pip3 --user install ansible`
* [openshift-restclient-python][openshift-restclient-python.git] >= 0.8.2
  * `pip3 --user install openshift`

## Source Code

* [modules](https://github.com/ansible/ansible/tree/devel/lib/ansible/modules/cloud/kubevirt)
  * [module_utils](https://github.com/ansible/ansible/blob/devel/lib/ansible/module_utils/kubevirt.py)
* [inventory plugin](https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/inventory/kubevirt.py)
* [unit tests](https://github.com/ansible/ansible/tree/devel/test/units/modules/cloud/kubevirt)
  * [fixtures](https://github.com/ansible/ansible/blob/devel/test/units/utils/kubevirt_fixtures.py)


## Testing

There are two target of tests that can be found here:
* module tests in [tests/playbooks](tests/playbooks)
* role tests in [tests/roles](tests/roles)

To run a full complement of tests for a given target please use the relevant `all.yml` playbook.


### Automatic testing

#### Unit tests

[Upstream ansible repository](ansible.git) contains unit tests covering the kubevirt modules.

#### Integration tests

Module tests ([tests/playbooks/all.yml](tests/playbooks/all.yml) are run against actual clusters with both
[KubeVirt](kubevirt.git) and [CDI](cdi.git) deployed, on top of:
- TravisCI (ubuntu vms supporting only minikube; no kvm acceleration for KubeVirt vms)
- oVirt Jenkins (physical servers that run any cluster [kubevirtci](kubevirtci.git) supports)

Module tests are run using:
- most recently released ansible (whatever one gets with `pip install ansible`)
- ansible stable branch(es)
- ansible devel branch

Role tests ([tests/roles/all.yml](tests/roles/all.yml)) are only run on TravisCI using the devel branch.

To detect regressions early, Travis runs all the tests every 24 hours against a fresh clone of ansible.git
and emails kubevirt module developers if tests fail.


### Manual testing

1. Clone this repository to a machine where you can `oc login` to your cluster:

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

   If you skipped the previous step, you might need to prepend that command with `sudo`.

9. Install ansible (in one of the many ways):

   * Install the [latest released version](https://github.com/ansible/ansible/releases):

     ```shell
     $ pip install ansible
     ```

     Again, `sudo` might be required here.
    
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
   $ ansible-playbook tests/playbooks/all.yml
   ```

   >**Note**: The playbook examples include [cloud-init](http://cloudinit.readthedocs.io/en/latest/) configuration to be able to access the created VMIs.

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

      It might take a while for the VM to come up before SSH can be used.

   2. For using `virtctl`:

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


#### Notes on `kubevirt_cdi_upload` module

To upload an image from localhost by using the `kubevirt_cdi_upload` module, your system needs to be able to connect to the [cdi upload proxy pod](https://github.com/kubevirt/containerized-data-importer/blob/master/doc/upload.md). This can be achieved by either:

1. Exposing the `cdi-uploadproxy` Service from the `cdi` namespace, or

2. Using `kubectl port-forward` to set up a temporary port forwarding through the Kubernetes API server: `kubectl port-forward -n cdi service/cdi-uploadproxy 9443:443`

### Notes on the `k8s_facts` module

The following command will collect facts about the existing VM(s), if there are any, and print out a JSON document based on [KubeVirt VM spec](https://kubevirt.io/api-reference/master/definitions.html#_v1_virtualmachine):

```shell
$ ansible-playbook examples/playbooks/k8s_facts_vm.yml
```

### Notes on the KubeVirt inventory plugin
Inventory plugins allow users to point at data sources to compile the inventory of hosts that Ansible uses to target tasks, either via the `-i /path/to/file` and/or `-i 'host1, host2'` command line parameters or from other configuration sources.

#### Enabling the KubeVirt inventory plugin
To enable the KubeVirt plugin, add the following section in the `tests/ansible.cfg` file:

```
[inventory]
enable_plugins = kubevirt
```

#### Configuring the KubeVirt inventory plugin
Define the plugin configuration in `tests/playbooks/plugin/kubevirt.yaml` as follows:

```
plugin: kubevirt
connections:
  - namespaces:
      - default
    interface_name: default
```

In this example, the KubeVirt plugin will list all VMIs from the `default` namespace and use the `default` interface name.

#### Using the KubeVirt inventory plugin
To use the plugin in a playbook, run:

```
$ ansible-playbook -i kubevirt.yaml <playbook>
```

>**Note**: The KubeVirt inventory plugin is designed to work with [Multus][multus.git]. It can be used only for VMIs, which are connected to the bridge and display the IP address in the Status field. For VMIs exposed by Kubernetes services, please use the [k8s Ansible module](https://docs.ansible.com/ansible/latest/plugins/inventory/k8s.html).

[multus.git]: https://github.com/intel/multus-cni

