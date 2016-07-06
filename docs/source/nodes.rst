AIOrchestra. OpenSource OpenStack TOSCA orchestration plugin. Nodes.
====================================================================


tosca.nodes.openstack.authorization
-----------------------------------

This node represents authorization mechanism for OpenStack using Keystone and its service catalog.
Type definition: `tosca.nodes.openstack.authorization`_

Properties::

    username - OpenStack user name
    password - OpenStack user password
    project_name - OpenStack user project name
    auth_url - OpenStack Keystone auth URL
    region_name - OpenStack auth region
    user_domain_name - OpenStack user domain name
    project_domain_name - OpenStack user project domain name

Attributes::

    auth_properties - represents auth properties mapping for further authorization purposes
    auth_token - represents auth token for passwordless authorization

Capabilities::

    tosca.capabilities.openstack.auth.attachable - means that this node can be attached to any other node



tosca.nodes.openstack.ssh_keypair
---------------------------------

This node represents OpenStack Nova SSH key pair.
Type definition: `tosca.nodes.openstack.ssh_keypair`_
Properties::

      use_connection_pool - this property passed not Nova client
      compute_api_version - Nova compute API version
      use_existing - weather to use existing key or create a new one
      name - SSH key pair name
      public_key - SSH public key

Attributes::

      id - SSH key ID
      name - SSH key name
      public_key - SSH public key
      private_key_content - SSH private key content


tosca.nodes.openstack.compute
-----------------------------

This node represents OpenStack Nova compute instance.
Type definition: `tosca.nodes.openstack.compute`_
Properties::

    use_connection_pool - this property passed not Nova client
    compute_api_version - Nova compute API version
    compute_name - Nova Compute instance future name
    compute_id - existing Nova compute instance ID
    availability_zone - Nova compute instance availability zone
    config_drive - weather to use config drive during boot or not

Attributes::

    compute_id - Nova compute instance ID
    networks - attached networks
    ports - attached network ports


Capabilities::

    host - represents capacity details (i.e - flavor)
    binding - represents network binding
    os - represents Operating system distron details
    scalable - weather node is scalable or not


Artifacts::

    image_ref - represents Glance image ID
    userdata - represents Nova boot userdata script


tosca.nodes.openstack.network
-----------------------------

This node represents OpenStack Neutron network.
Type definition: `tosca.nodes.openstack.network`_
Properties::

    is_external - weather network is has access to internet
    network_name - Neutron network name
    network_id - existing Neutron network ID

Attributes::

    network_id - Neutron network ID
    network_name - Neutron network name
    subnets - Neutron network subnets

Capabilities::

    link - meas that this node can be linked to others

tosca.nodes.openstack.network.subnet
------------------------------------

This node represents OpenStack Neutron network subnet.
Type definition: `tosca.nodes.openstack.network.subnet`_
Properties::

    ip_version - subnet IP version
    cidr - subnet CIDR
    start_ip - pool range start IP
    end_ip - pool range end IP
    gateway_ip - subnet gateway IP
    network_name - subnet name
    network_id - existing subnet ID
    segmentation_id - subnet segmentation ID
    network_type - network type
    physical_network - physical network
    dhcp_enabled - weather is to enable DHCP for subnet or not
    dns_nameservers - DNS name servers

Attributes::

    link_id - linked network ID
    network_id - subnet ID
    network_name - subnet name


Capabilities::

    link - meas that this node can be linked to others

Requirements::

    link - network link requirement

tosca.nodes.openstack.network.port
----------------------------------

This node represents OpenStack Neutron network port.
Type definition: `tosca.nodes.openstack.network.port`_
Properties::

    port_name - name to assign
    port_id - existing port ID
    ip_address - IP address to assign
    order - assign order to compute instance
    is_default - weather if this port is default
    ip_range_start - lower bound of IP address
    ip_range_end - upper bound of IP address

Attributes::

    ip_address - port IP address

Requirements::

    binding - to which node port must be assigned
    link - to each network/subnet this port belongs

tosca.nodes.openstack.network.router
------------------------------------

This node represents OpenStack Neutron network router.
Type definition: `tosca.nodes.openstack.network.router`_
Properties::

    router_name - name to assign
    router_id - existing router ID

Attributes::

    router_id - router ID

Capabilities::

    link - means router can be assigned to networks

Requirements::

    link - actual network link


tosca.nodes.openstack.network.floating_ip
-----------------------------------------

This node represents OpenStack Neutron network floating IP.
Type definition: `tosca.nodes.openstack.network.floating_ip`_
Properties::

    floating_ip_id - existing floatin IP ID

Attributes::

    fixed_ip_address - port internal fixed IP address
    floating_ip_address - floating IP address
    port_id - assigned port ID
    router_id - router ID to which network with floating pool attached

Capabilities::

    binding - means floating IP can be attached

Requirements::

    link - network with floating pool
    binding - port to attach floating IP


tosca.nodes.openstack.network.port.security_group
-------------------------------------------------

This node represents OpenStack Neutron network port security group.
Type definition: `tosca.nodes.openstack.network.port.security_group`_
Properties::

    security_group_name - name to assign
    security_group_id - existing security group ID
    description - security group description

Attributes::

    security_group_id - security group ID


tosca.nodes.openstack.network.port.security_group.rule
------------------------------------------------------

This node represents OpenStack Neutron network port security group rule.
Type definition: `tosca.nodes.openstack.network.port.security_group.rule`_
Properties::

    direction - ingress or egress direction
    ethertype - IP version
    port_range_min - access port range lower bound
    port_range_max - access port range upper bound
    protocol - OSI transport layer protocol
    remote_ip_prefix - CIDR


tosca.nodes.openstack.network.load_balancer
-------------------------------------------

This node represents OpenStack Neutron subnet IP range load balancer.
Type definition: `tosca.nodes.openstack.network.load_balancer`_
Properties::

    algorithm
    protocol
    protocol_port

Capabilities::

    client - means load balancer can be used by specific network link

Requirements::

    application - compute instance

tosca.nodes.openstack.compute.file
----------------------------------

This node represents OpenStack Nova injection file.
Type definition: `tosca.nodes.openstack.compute.file`_
Properties::

    source - local file path
    destination - remote file path where source file will be injected


.. _tosca.nodes.openstack.authorization: https://github.com/aiorchestra/aiorchestra-openstack-plugin/blob/master/types.yaml#L9-L47
.. _tosca.nodes.openstack.ssh_keypair: https://github.com/aiorchestra/aiorchestra-openstack-plugin/blob/master/types.yaml#L53-L90
.. _tosca.nodes.openstack.compute: https://github.com/aiorchestra/aiorchestra-openstack-plugin/blob/master/types.yaml#L96-L180
.. _tosca.nodes.openstack.network: https://github.com/aiorchestra/aiorchestra-openstack-plugin/blob/master/types.yaml#L187-L235
.. _tosca.nodes.openstack.network.subnet: https://github.com/aiorchestra/aiorchestra-openstack-plugin/blob/master/types.yaml#L241-L357
.. _tosca.nodes.openstack.network.port: https://github.com/aiorchestra/aiorchestra-openstack-plugin/blob/master/types.yaml#L363-L449
.. _tosca.nodes.openstack.network.router: https://github.com/aiorchestra/aiorchestra-openstack-plugin/blob/master/types.yaml#L455-L504
.. _tosca.nodes.openstack.network.floating_ip: https://github.com/aiorchestra/aiorchestra-openstack-plugin/blob/master/types.yaml#L510-L549
.. _tosca.nodes.openstack.network.port.security_group: https://github.com/aiorchestra/aiorchestra-openstack-plugin/blob/master/types.yaml#L555-L576
.. _tosca.nodes.openstack.network.port.security_group.rule: https://github.com/aiorchestra/aiorchestra-openstack-plugin/blob/master/types.yaml#L578-L615
.. _tosca.nodes.openstack.network.load_balancer: https://github.com/aiorchestra/aiorchestra-openstack-plugin/blob/master/types.yaml#L621-L655
.. _tosca.nodes.openstack.compute.file: https://github.com/aiorchestra/aiorchestra-openstack-plugin/blob/master/types.yaml#L661-L674
