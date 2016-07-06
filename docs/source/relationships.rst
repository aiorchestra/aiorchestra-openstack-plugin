AIOrchestra. OpenSource OpenStack TOSCA orchestration plugin. Relationships.
============================================================================


tosca.relationships.openstack.inject_auth
-----------------------------------------

This relationship must be used with every OpenStack node type in requirements for authorization purposes
Allowed target type: `tosca.nodes.openstack.authorization`_

tosca.relationships.openstack.ssh_keypair_provider
--------------------------------------------------

This relationship must be used whenever SSH key attributes are required
Allowed target type: `tosca.nodes.openstack.ssh_keypair`_

tosca.relationships.openstack.compute.injected_with
---------------------------------------------------

This relationship must be used for compute boot file injection
Allowed target type: `tosca.nodes.openstack.compute.file`_

tosca.relationships.openstack.network.linked
--------------------------------------------

This relationship must be used for network linkin
Allowed target type: `tosca.nodes.openstack.network`_, `tosca.nodes.openstack.network.subnet`_

tosca.relationships.openstack.compute.port.bind
-----------------------------------------------

This relationship must be used for port binding to compute instance
Allowed target type: `tosca.nodes.openstack.compute`_

tosca.relationships.openstack.network.port.bind
-----------------------------------------------

This relationship must be used for binding compute instance to port
Allowed target type: `tosca.nodes.openstack.network.port`_

tosca.relationships.openstack.network.router.bind
-------------------------------------------------

This relationship must used for binding network to router
Allowed target type: `tosca.nodes.openstack.network`_

tosca.relationships.openstack.network.router.link
-------------------------------------------------

This relationship must be used for linking subnet to router
Allowed target type: `tosca.nodes.openstack.network.subnet`_

tosca.relationships.openstack.network.floating_ip.provider
----------------------------------------------------------

This relationship must be used whenever floating IP address is needed
Allowed target types: `tosca.nodes.openstack.network.floating_ip`_

tosca.relationships.openstack.network.floating_ip
-------------------------------------------------

This relationship must be used when picking network with floating pool
Allowed target type: `tosca.nodes.openstack.network`_

tosca.relationships.openstack.network.port.floating_ip
------------------------------------------------------

This relationship must be used for attaching floating IP to port
Allowed target type: `tosca.nodes.openstack.network.port`_

tosca.relationships.openstack.network.port.security_group.rule
--------------------------------------------------------------

This relationship must be used for attaching rule to security group
Allowed target types: `tosca.nodes.openstack.network.port.security_group.rule`_

tosca.relationships.openstack.network.port.security_group.attached
------------------------------------------------------------------

This relationship must be used for attaching security group to port
Allowed target type: `tosca.nodes.openstack.network.port.security_group`_

tosca.relationships.openstack.network.load_balancer.member
----------------------------------------------------------

This relationship must be used for attaching compute instances to load balancer
Allowed target types: `tosca.nodes.openstack.compute`_


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
