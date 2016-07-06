AIOrchestra. OpenSource OpenStack TOSCA orchestration plugin
============================================================


TOSCA simple profile
--------------------

AIOrchestra OpenStack plugin relays on `TOSCA simple profile`_ as bases.
Plugin has several categories of types::

    node types
    artifacts
    capabilities
    relationships


Types
-----

AIOrchestra OpenStack plugin implements next node types::

    tosca.nodes.openstack.authorization
    tosca.nodes.openstack.ssh_keypair
    tosca.nodes.openstack.compute
    tosca.nodes.openstack.network
    tosca.nodes.openstack.network.subnet
    tosca.nodes.openstack.network.port
    tosca.nodes.openstack.network.router
    tosca.nodes.openstack.network.floating_ip
    tosca.nodes.openstack.network.port.security_group
    tosca.nodes.openstack.network.port.security_group.rule
    tosca.nodes.openstack.network.load_balancer
    tosca.nodes.openstack.compute.file

AIOrchestra OpenStack plugin implements next artifacts::

    tosca.artifacts.openstack.image
    tosca.artifacts.openstack.compute.injection_file
    tosca.artifacts.openstack.compute.userdata

AIOrchestra OpenStack plugin implements next ralationships::

    tosca.relationships.openstack.inject_auth
    tosca.relationships.openstack.ssh_keypair_provider
    tosca.relationships.openstack.compute.injected_with
    tosca.relationships.openstack.network.linked
    tosca.relationships.openstack.compute.port.bind
    tosca.relationships.openstack.network.port.bind
    tosca.relationships.openstack.network.router.bind
    tosca.relationships.openstack.network.router.link
    tosca.relationships.openstack.network.floating_ip.provider
    tosca.relationships.openstack.network.floating_ip
    tosca.relationships.openstack.network.port.floating_ip
    tosca.relationships.openstack.network.port.security_group.rule
    tosca.relationships.openstack.network.port.security_group.attached
    tosca.relationships.openstack.network.load_balancer.member

AIOrchestra OpenStack plugin implements next ralationships::

    tosca.capabilities.openstack.network.load_balancer.endpoint
    tosca.capabilities.openstack.network.load_balancer.member.endpoint
    tosca.capabilities.openstack.network.port.bindable
    tosca.capabilities.openstack.network.port.security_group.attachable
    tosca.capabilities.openstack.network.port.security_group.rule.attachable
    tosca.capabilities.openstack.auth.attachable
    tosca.capabilities.openstack.compute.ssh.attachable
    tosca.capabilities.openstack.flavor


Types definition can be found `here`_.


.. _TOSCA simple profile: http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/TOSCA-Simple-Profile-YAML-v1.0.pdf
.. _here: https://github.com/aiorchestra/aiorchestra-openstack-plugin/blob/master/types.yaml
