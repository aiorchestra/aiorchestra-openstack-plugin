AIOrchestra. OpenSource OpenStack TOSCA orchestration
=====================================================


What is TOSCA?
--------------

The TOSCA Simple Profile in `YAML`_ specifies a rendering of TOSCA which aims
to provide a more accessible syntax as well as a more concise and incremental
expressiveness of the TOSCA DSL in order to minimize the learning curve and
speed the adoption of the use of TOSCA to portably describe cloud applications.
This proposal describes a `YAML`_ rendering for TOSCA. `YAML`_ is a human friendly data
serialization standard with a syntax much easier to read and edit
than XML. As there are a number of DSLs encoded in `YAML`_, a `YAML`_ encoding of the TOSCA
DSL makes TOSCA more accessible by these communities.
This proposal prescribes an isomorphic rendering in `YAML`_ of a subset of the
TOSCA v1.0 ensuring that TOSCA semantics are preserved and can be transformed
from XML to `YAML`_ or from `YAML`_ to XML. Additionally, in order to streamline the
expression of TOSCA semantics, the `YAML`_ rendering is sought to be more concise and
compact through the use of the `YAML`_ syntax.

More information can be regarding TOSCA simple profile can be found at its `home page`_.


What is OpenStack?
------------------

Feel free to find lots of articles and posts regarding this question.
But the most authoritative is `OpenStack official web site`_.


.. _YAML: http://yaml.org/
.. _home page: http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/TOSCA-Simple-Profile-YAML-v1.0.pdf
.. _OpenStack official web site: https://opensource.com/resources/what-is-openstack
