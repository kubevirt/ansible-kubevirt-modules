KubeVirt application deployment
===============================

The `kubevirt.app_deployment` role manages the hybrid application infrastructure.
You can manage the virtual machines together with deployments and services.

Requirements
------------

 * Ansible version 2.8 or higher
 * openshift SDK version 0.8.6 or higher

Role Variables
--------------

| Name                          | Default value |                                                    |
|-------------------------------|---------------|----------------------------------------------------|
| kubevirt_app_vms              | UNDEF         | Virtual machine applications specification.        |
| kubevirt_app_services         | UNDEF         | Services for the virtual machines and deployments. |
| kubevirt_app_deployments      | UNDEF         | Deployments applications specification.            |
| kubevirt_app_network_policies | UNDEF         | By default, all vmis in a namespace are accessible from other vmis and network endpoints. To isolate one or more vmis in a project, you can create NetworkPolicy objects in that namespace to indicate the allowed incoming connections. Note that your networking solution must support NetworkPolicy. |

`kubevirt_app_vms`

| Name      | Default value |                                              |
|-----------|---------------|----------------------------------------------|
| name      | UNDEF         | Name of the virtual machine.                 |
| affinity  | UNDEF         | Describes node affinity scheduling rules for the vm. |
| node_affinity | UNDEF     | Describes vm affinity scheduling rules e.g. co-locate this vm in the same node, zone, etc. as some other vms |
| anti_affinity | UNDEF     | Describes vm anti-affinity scheduling rules e.g. avoid putting this vm in the same node, zone, etc. as some other vms. |
| hostname  | UNDEF         | Specifies the hostname of the virtual machine. The hostname will be set either by dhcp, cloud-init if configured or virtual machine name will be used. |
| subdomain | UNDEF         | If specified, the fully qualified virtual machine hostname will be "hostname.subdomain.namespace.svc.cluster_domain". If not specified, the virtual machine will not have a domain name at all. The DNS entry will resolve to the virtual machine, no matter if the vmi itself can pick up a hostname. |
| image | UNDEF | Dictionary specifing the image of the virtual machine. The dictionary can contain <i>url</i> and <i>storage</i> keys. <i>url</i> defines the qcow image to be used as datavolume source and <i>storage</i> defines the size of the volume to be created. |
| wait | true | If <i>true</i> wait for the virtual machine to be in requested state. |
| state | UNDEF | Set the virtual machine to either <i>present</i>, <i>absent</i>, <i>running</i> or <i>stopped</i>. |
| namespace | UNDEF | Use to specify an vm namespace. |
| memory | UNDEF | The amount of memory to be requested by virtual machine. For example 1024Mi. |
| template | UNDEF | Name of template to be used for virtual machine. |
| disks | UNDEF | List of dictionaries which specify disks of the virtual machine. A disk can be made accessible via four different types: <i>disk</i>, <i>lun</i>, <i>cdrom</i>, <i>floppy</i>. All possible configuration options are available <a href="https://kubevirt.io/api-reference/master/definitions.html#_v1_disk">here</a>. Each disk must have specified a <i>volume</i> that declares which volume type of the disk. All possible configuration options of volume are available <a href="https://kubevirt.io/api-reference/master/definitions.html#_v1_volume">here</a>. |
| interfaces | UNDEF | An interface defines a virtual network interface of a virtual machine (also called a frontend). All possible configuration options interfaces are available in <a href="https://kubevirt.io/api-reference/master/definitions.html#_v1_interface">interfaces</a>. Each interface must have specified a <i>network</i> that declares which logical or physical device it is connected to (also called as backend). All possible configuration options of network are available in <a href="https://kubevirt.io/api-reference/master/definitions.html#_v1_network">networks</a>. |
| cloud_init_nocloud | UNDEF | Represents a cloud-init NoCloud user-data source. The NoCloud data will be added as a disk to the virtual machine. A proper cloud-init installation is required inside the guest. More information: <a href="https://kubevirt.io/api-reference/master/definitions.html#_v1_cloudinitnocloudsource">cloud init</a> |
| wait_timeout | UNDEF | The amount of time in seconds the module should wait for the resource to get into desired state. |

`kubevirt_app_services`

| Name          | Default value |                                     |
|---------------|---------------|-------------------------------------|
| name          | UNDEF         | Name of the service.                |
| namespace     | UNDEF         | Namespace of the service.           |
| labels        | UNDEF         | Labels of the service.              |
| selector      | UNDEF         | Label selectors identify objects this Service should apply to. |
| ports         | UNDEF         | A list of <a href="https://kubernetes.io/docs/concepts/services-networking/service/#multi-port-services">ports</a> to expose.  |

`kubevirt_app_deployments`

| Name              | Default value |                                            |
|-------------------|---------------|--------------------------------------------|
| name              | UNDEF         | Name of the deployment.                |
| namespace         | UNDEF         | Namespace of the deployment.           |
| labels            | UNDEF         | Labels of the deployments. Deployment pods are labeled by this label and match label selector is created for them. |
| annotations       | UNDEF         | Annotations of the deployment.         |
| replicas          | UNDEF         | Number of replicas to be running.      |
| max_surge         | UNDEF         | Specifies the maximum number of Pods that can be created over the desired number of Pods. |
| max_unavailable   | UNDEF         | Specifies the maximum number of Pods that can be unavailable during the update process. |
| containers        | UNDEF         | List of dictionaries specifyng the containers to be created. The dictionary can contain <i>name</i>, <i>image</i> and <i>ports</i> which define the name, image and ports of the container. |

`kubevirt_app_network_policies`

| Name                 | Default value |                                            |
|----------------------|---------------|--------------------------------------------|
| name                 | UNDEF         | Name of the network policy.                |
| pod_selector         | UNDEF         | Dict of pod labels to which the policy apply. When empty selects all pods in policy's namespace. |
| deny_all             | UNDEF         | If true deny all ingress and egress trafic to/from virtual machines. |
| ingress              | UNDEF         | List of specific ingress rules for VMIs. |
| ingress_allow_all    | UNDEF         | If true allow all ingress trafic to virtual machines. |
| ingress_deny_all     | UNDEF         | If true all ingress trafic to virtual machines will be denied. |
| ingress_allow_same_namespace | UNDEF | If true only ingress trafic from same namespace will be allowed. |
| egress               | UNDEF         | List of specific egress rules for VMIs. |
| egress_allow_all     | UNDEF         | If true allow all egress trafic to virtual machines. |
| egress_deny_all      | UNDEF         | If true all egress trafic to virtual machines will be denied. |
| egress_allow_same_namespace | UNDEF  | If true only egress trafic from same namespace will be allowed. |

`ingress`

| Name                 | Default value |                                            |
|----------------------|---------------|--------------------------------------------|
| ip_blocks    | UNDEF         | This selects particular IP CIDR ranges to allow as ingress sources. These should be cluster-external IPs, since VMI IPs are ephemeral and unpredictable |
| namespace_selector | UNDEF   | This selects particular namespaces for which all Pods should be allowed as egress destinations. |
| pod_selector | UNDEF         | Specify vmis to which the ingress rules apply. |
| ports        | UNDEF         | Define ports and protocol of the ports to be allowed by ingress traffic. |

`egress`

| Name                 | Default value |                                            |
|----------------------|---------------|--------------------------------------------|
| ip_blocks     | UNDEF         | This selects particular IP CIDR ranges to allow as ingress sources. These should be cluster-external IPs, since VMI IPs are ephemeral and unpredictable |
| namespace_selector | UNDEF    | This selects particular namespaces for which all Pods should be allowed as egress destinations. |
| pod_selector  | UNDEF         | Specify vmis to which the egress rules apply. |
| ports         | UNDEF         | Define ports and protocol of the ports to be allowed by egress traffic. |

Dependencies
------------

None.

Example Playbook
----------------
See [example playbooks](https://github.com/kubevirt/ansible-kubevirt-modules/blob/master/roles/app_deployment/examples).

License
-------

Apache License 2.0
