#    Author: Denys Makogon
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from aiorchestra.tests import base as aiorchestra

from openstack_plugin.tests.integration import base
from openstack_plugin.tests.integration import config


class TestComplex(base.BaseAIOrchestraOpenStackTestCase):

    def setUp(self):
        super(TestComplex, self).setUp()

    def tearDown(self):
        super(TestComplex, self).tearDown()

    @aiorchestra.with_deployed('orchestra-openstack-compute-'
                               'with-floating-ip.yaml',
                               inputs=config.CONFIG)
    def test_compute_with_floating_ip(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-network-subnet-'
                               'port-attached-to-compute-with-sgs.yaml',
                               inputs=config.CONFIG)
    def test_compute_with_port_and_security_group(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-network-'
                               'subnet-port-attached-to-compute.yaml',
                               inputs=config.CONFIG)
    def test_network_subnet_and_port_to_compute(self, context):
        pass

    @aiorchestra.with_deployed(
        'orchestra-openstack-network-subnet-'
        'router-two-ports-attached-to-compute.yaml',
        inputs=config.CONFIG)
    def test_ext_net_router_network_subnet_and_two_ports_to_compute(
            self, context):
        pass

    @aiorchestra.with_deployed(
        'orchestra-openstack-network-subnet-'
        'two-ports-attached-to-compute.yaml',
        inputs=config.CONFIG)
    def test_network_subnet_and_two_ports_to_compute(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-vrouter-base.yaml',
                               inputs=config.CONFIG)
    def test_vrouter_base(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-vrouter-'
                               'base-with-two-computes.yaml',
                               inputs=config.CONFIG)
    def test_vrouter_base_with_two_computes(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-vrouter-'
                               'base-with-external-access.yaml',
                               inputs=config.CONFIG)
    def test_vrouter_base_with_external_access(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-load-balancer.yaml',
                               inputs=config.CONFIG)
    def test_lbaas(self, context):
        pass
