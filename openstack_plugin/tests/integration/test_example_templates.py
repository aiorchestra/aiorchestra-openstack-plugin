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

from aiorchestra.tests import base

from openstack_plugin.tests.integration import config


class BaseAIOrchestraOpenStackTestCase(base.BaseAIOrchestraTestCase):
    tosca_directory = base.os.path.join(
        base.os.path.dirname(
            base.os.path.abspath(__file__)), '../../../examples')


class TestExamples(BaseAIOrchestraOpenStackTestCase):

    def setUp(self):
        super(TestExamples, self).setUp()

    def tearDown(self):
        super(TestExamples, self).tearDown()

    @base.with_deployed('orchestra-openstack-authorization.yaml',
                        inputs=config.CONFIG)
    def test_authorize_template(self, context):
        pass

    @base.with_deployed('orchestra-openstack-ssh-keypair.yaml',
                        inputs=config.CONFIG)
    def test_ssh_keypair_template(self, context):
        pass

    @base.with_deployed('orchestra-compute-node.yaml',
                        inputs=config.CONFIG)
    def test_compute_deploy(self, context):
        pass

    @base.with_deployed('orchestra-compute-node-with-ssh-keypair.yaml',
                        inputs=config.CONFIG)
    def test_compute_with_ssh_deploy(self, context):
        pass

    @base.with_deployed('orchestra-openstack-network.yaml',
                        inputs=config.CONFIG)
    def test_network(self, context):
        pass

    @base.with_deployed('orchestra-openstack-network-with-subnet.yaml',
                        inputs=config.CONFIG)
    def test_subnet(self, context):
        pass

    @base.with_deployed('orchestra-openstack-network-'
                        'with-subnet-and-port.yaml',
                        inputs=config.CONFIG)
    def test_subnet_port(self, context):
        pass

    @base.with_deployed('orchestra-openstack-router.yaml',
                        inputs=config.CONFIG)
    def test_router(self, context):
        pass

    @base.with_deployed('orchestra-openstack-router-networks-subnets.yaml',
                        inputs=config.CONFIG)
    def test_router_with_two_subnets(self, context):
        pass

    @base.with_deployed('orchestra-openstack-router-with-ext-net-'
                        'and-internal-networks-subnets.yaml',
                        inputs=config.CONFIG)
    def test_router_with_ext_net_and_two_subnets(self, context):
        pass

    @base.with_deployed('orchestra-openstack-compute-and-router-'
                        'with-ext-net-and-internal-networks-subnets.yaml',
                        inputs=config.CONFIG)
    def test_compute_and_router_with_ext_net_and_two_subnets(
            self, context):
        pass

    @base.with_deployed('orchestra-openstack-two-computes-and-router-'
                        'with-ext-net-and-internal-networks-subnets.yaml',
                        inputs=config.CONFIG)
    def test_two_compute_and_router_with_ext_net_and_two_subnets(
            self, context):
        pass

    @base.with_deployed('orchestra-openstack-router-with-ext-net-'
                        'fip-and-internal-networks-subnets-ports.yaml',
                        inputs=config.CONFIG)
    def test_ext_net_fip_router_network_subnet_port(self, context):
        pass

    @base.with_deployed('orchestra-openstack-compute-and-router-with-'
                        'ext-net-fip-and-internal-networks-subnets.yaml',
                        inputs=config.CONFIG)
    def test_two_compute_and_router_with_ext_net_fip_and_two_subnets(
            self, context):
        pass

    @base.with_deployed('orchestra-openstack-vrouter-base.yaml',
                        inputs=config.CONFIG)
    def test_vrouter_base(self, context):
        pass

    @base.with_deployed('orchestra-openstack-vrouter-base-'
                        'with-two-computes-attached.yaml',
                        inputs=config.CONFIG)
    def test_vrouter_base_with_two_computes_attached(self, context):
        pass

    @base.with_deployed('orchestra-openstack-security-group.yaml',
                        inputs=config.CONFIG)
    def test_security_group(self, context):
        pass

    @base.with_deployed('orchestra-openstack-router-with-ext-net-'
                        'fip-and-internal-networks-'
                        'subnets-ports-and-sg.yaml',
                        inputs=config.CONFIG)
    def test_ext_net_fip_router_network_subnet_port_sg(self, context):
        pass
