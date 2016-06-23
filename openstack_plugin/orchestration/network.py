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

from aiorchestra.core import utils

from openstack_plugin.common import clients


@utils.operation
async def create(node, inputs):
    node.context.logger.info(
        '[{0}] - Attempting to create network.'.format(node.name))
    neutron = clients.openstack.neutron(node)
    if not node.properties['use_existing']:
        network = {'name': node.properties['name_or_id'],
                   'admin_state_up': True}
        net = neutron.create_network({'network': network})
    else:
        node.context.logger.info(
            '[{0}] - Using existing network.'.format(node.name))
        net = neutron.show_network(node.properties['name'])
    node.batch_update_runtime_properties(**net['network'])
    node.context.logger.info(
        '[{0}] - Network "{1}" created.'.format(
            node.name, node.properties['name_or_id']))


@utils.operation
async def delete(node, inputs):
    node.context.logger.info(
        '[{0}] - Attempting to delete network.'.format(node.name))
    task_retries = inputs.get('task_retries', 10)
    task_retry_interval = inputs.get('task_retry_interval', 10)
    neutron = clients.openstack.neutron(node)
    if not node.properties['use_existing']:
        neutron.delete_network(node.attributes['id'])

    def is_gone():
        try:
            neutron.show_network(node.attributes['id'])
            return False
        except Exception as ex:
            node.context.logger.debug(str(ex))
            return True
    await utils.retry(is_gone, exceptions=(Exception, ),
                      task_retries=task_retries,
                      task_retry_interval=task_retry_interval)
    node.context.logger.info(
        '[{0}] - Network "{1}" deleted.'.format(
            node.name, node.properties['name_or_id']))
