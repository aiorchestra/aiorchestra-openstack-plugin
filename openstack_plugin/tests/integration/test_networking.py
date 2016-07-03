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


class TestNetworking(base.BaseAIOrchestraOpenStackTestCase):

    def setUp(self):
        super(TestNetworking, self).setUp()

    def tearDown(self):
        super(TestNetworking, self).tearDown()

    @aiorchestra.with_deployed('orchestra-openstack-network.yaml',
                               inputs=config.CONFIG)
    def test_network(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-network-subnet.yaml',
                               inputs=config.CONFIG)
    def test_subnet(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-network-port.yaml',
                               inputs=config.CONFIG)
    def test_network_port(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-network-'
                               'subnet-port.yaml',
                               inputs=config.CONFIG)
    def test_subnet_port(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-router.yaml',
                               inputs=config.CONFIG)
    def test_router(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-floating-ip.yaml',
                               inputs=config.CONFIG)
    def test_floating_ip(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-security-group.yaml',
                               inputs=config.CONFIG)
    def test_security_group(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-network-'
                               'subnet-port-sgs.yaml',
                               inputs=config.CONFIG)
    def test_port_with_security_group(self, context):
        pass
