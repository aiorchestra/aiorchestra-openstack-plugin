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


class TestCompute(base.BaseAIOrchestraOpenStackTestCase):

    def setUp(self):
        super(TestCompute, self).setUp()

    def tearDown(self):
        super(TestCompute, self).tearDown()

    @aiorchestra.with_deployed('orchestra-openstack-ssh-keypair.yaml',
                               inputs=config.CONFIG)
    def test_ssh_keypair_template(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-compute.yaml',
                               inputs=config.CONFIG)
    def test_compute_deploy(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-compute-with-ssh.yaml',
                               inputs=config.CONFIG)
    def test_compute_with_ssh_deploy(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-compute-'
                               'with-userdata.yaml',
                               inputs=config.CONFIG)
    def test_compute_with_userdata(self, context):
        pass

    @aiorchestra.with_deployed('orchestra-openstack-compute-'
                               'with-file-injection.yaml',
                               inputs=config.CONFIG)
    def test_compute_with_injections_capability(self, context):
        pass

    @aiorchestra.with_deployed(
        'orchestra-openstack-compute-'
        'with-file-injection-alternative.yaml',
        inputs=config.CONFIG)
    def test_compute_with_injections_node(self, context):
        pass
