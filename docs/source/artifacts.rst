AIOrchestra. OpenSource OpenStack TOSCA orchestration plugin. Artifacts.
========================================================================


tosca.artifacts.openstack.image
-------------------------------

Artifact `tosca.artifacts.openstack.image`_ represents Glance image.
Properties::

    image - Glane image ID


tosca.artifacts.openstack.compute.injection_file
------------------------------------------------

Artifact `tosca.artifacts.openstack.compute.injection_file`_ represents injection file (alternative to file injection node type).
Properties::

    source - local file path
    destination - remote path to inject source file


tosca.artifacts.openstack.compute.userdata
------------------------------------------

Artifact `tosca.artifacts.openstack.compute.userdata`_ represents Nova boot user data script.
Properties::

    script - local file script path


.. _tosca.artifacts.openstack.image: https://github.com/aiorchestra/aiorchestra-openstack-plugin/blob/master/types.yaml#L680-L684
.. _tosca.artifacts.openstack.compute.injection_file: https://github.com/aiorchestra/aiorchestra-openstack-plugin/blob/master/types.yaml#L686-L692
.. _tosca.artifacts.openstack.compute.userdata: https://github.com/aiorchestra/aiorchestra-openstack-plugin/blob/master/types.yaml#L694-L698
