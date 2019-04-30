# Ansible KubeVirt Modules

Modules have been moved to [Ansible repository](https://github.com/ansible/ansible/tree/devel/lib/ansible/modules/cloud/kubevirt). This repo now only holds the integration tests of the modules.

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

### Environment for running playbooks

#### Image uploading from localhost (anything using kubevirt_cdi_upload module)

Your system needs to be able to connect to the [cdi upload proxy pod](https://github.com/kubevirt/containerized-data-importer/blob/master/doc/upload.md). This can be achieved by either:

1. Exposing the `cdi-uploadproxy` Service from the `cdi` namespace.

2. Using `kubectl port-forward` to set up temporary port forwarding through the kubernetes api server, like so: `kubectl port-forward -n cdi service/cdi-uploadproxy 9443:443`

### Facts

* Once one of the previous resources has been created, the facts module can be tested as well as follows:

```shell
$ ansible-playbook tests/playbooks/k8s_facts_vm.yml
```

The above command, will gather the information for the VM stated in the playbook and print out a JSON document based on [KubeVirt VM spec](https://kubevirt.io/api-reference/master/definitions.html#_v1_virtualmachine).


## KubeVirt Inventory plugin
Inventory plugins allow users to point at data sources to compile the inventory of hosts that Ansible uses to target tasks, either via the -i /path/to/file and/or -i 'host1, host2' command line parameters or from other configuration sources.

### Enabling KubeVirt inventory plugin
In your `ansible.cfg` file find option `enable_plugins` in `inventory` section and add there kubevirt:

```
[inventory]
enable_plugins = kubevirt
```

### Using KubeVirt inventory plugin
You need to create plugin configuration which specify which plugin to use, and some other parameters, which you want to use:

```
plugin: kubevirt
connections:
  - namespaces:
      - default
    interface_name: default
```

This configuration will use kubevirt plugin and will list all VMIs from default namespace and as default IP it will use network interface from default network.

### Execute the playbook with KubeVirt inventory plugin
To use the plugin in playbook, just pass it to `ansible-playbook` command in `-i` option:

```
$ ansible-playbook -i kubevirt.yaml myplaybook.yml
```

Note that KubeVirt inventory plugin is designed to work with multus, meaning the plugin is designed to work with VMIs which doesn't use Kubernetes service to expose it's network, but VMIs which are connected to bridge and report the reachable IP address in status field of VMI object. For VMIs exposed by Kubernetes services, please use [k8s](https://docs.ansible.com/ansible/latest/plugins/inventory/k8s.html).
