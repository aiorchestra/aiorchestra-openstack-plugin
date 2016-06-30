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

    @aiorchestra.with_deployed('orchestra-openstack-compute-and-router-'
                               'with-ext-net-and-internal-'
                               'networks-subnets.yaml',
                               inputs=config.CONFIG)
    def test_compute_and_router_with_ext_net_and_two_subnets(
            self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-two-'
                               'computes-and-router-'
                               'with-ext-net-and-internal-'
                               'networks-subnets.yaml',
                               inputs=config.CONFIG)
    def test_two_compute_and_router_with_ext_net_and_two_subnets(
            self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-compute-'
                               'and-router-with-'
                               'ext-net-fip-and-internal-networks-'
                               'subnets.yaml',
                               inputs=config.CONFIG)
    def test_two_compute_and_router_with_ext_net_fip_and_two_subnets(
            self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-'
                               'vrouter-base.yaml',
                               inputs=config.CONFIG)
    def test_vrouter_base(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-vrouter-base-'
                               'with-two-computes-attached.yaml',
                               inputs=config.CONFIG)
    def test_vrouter_base_with_two_computes_attached(self, context):
        pass
