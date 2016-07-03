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
from openstack_plugin.networking import network


@utils.operation
async def network_create(node, inputs):
    node.context.logger.info(
        '[{0}] - Attempting to create network.'.format(node.name))
    neutron = clients.openstack.neutron(node)
    network_name = node.properties.get('network_name')
    network_id = node.properties.get('network_id')
    is_external = node.properties['is_external']
    use_existing = True if network_id else False
    identifier = network_name if not network_id else network_id
    net = await network.create(
        node.context,
        identifier,
        neutron,
        is_external=is_external,
        admin_state_up=True,
        use_existing=use_existing,
    )

    node.batch_update_runtime_properties(**{
        'network_id': net['id'],
        'network_name': net['name'],
        'subnets': net['subnets']
    })
    node.context.logger.info(
        '[{0}] - Network "{1}" created.'.format(
            node.name, identifier))


@utils.operation
async def network_start(node, inputs):
    node.context.logger.info(
        '[{0}] - Attempting to start network.'.format(node.name))
    neutron = clients.openstack.neutron(node)
    net_id = node.get_attribute('network_id')
    net = neutron.show_network(net_id)['network']
    node.batch_update_runtime_properties(**{
            'network_id': net['id'],
            'network_name': net['name'],
            'subnets': net['subnets']
    })


@utils.operation
async def network_delete(node, inputs):
    node.context.logger.info(
        '[{0}] - Attempting to delete network.'.format(node.name))
    task_retries = inputs.get('task_retries', 10)
    task_retry_interval = inputs.get('task_retry_interval', 10)
    neutron = clients.openstack.neutron(node)
    net_id = node.get_attribute('network_id')
    use_existing = True if node.properties.get(
        'network_id') else False

    await network.delete(
        node.context,
        net_id,
        neutron,
        use_existing=use_existing,
        task_retries=task_retries,
        task_retry_interval=task_retry_interval
    )

    node.context.logger.info(
        '[{0}] - Network "{1}" deleted.'.format(
            node.name, net_id))


@utils.operation
async def link(source, target, inputs):
    source.context.logger.info(
        '[{0} -----> {1}] - Network "{2}" attached.'
        .format(target.name,
                source.name,
                target.get_attribute('network_id')))
    if 'link_id' in target.runtime_properties:
        link_id = target.runtime_properties['link_id']
        subnet_id = target.get_attribute('network_id')
        ip_version = target.runtime_properties['ip_version']
        source.context.logger.info(
            '[{0} -----> {1}] - It appears that target network '
            'is a subnet for network "{2}".'
            .format(target.name, source.name, link_id))
        source.batch_update_runtime_properties(**{
            'link_id': link_id,
            'subnet_id': subnet_id,
            'ip_version': ip_version,
        })
    else:
        source.update_runtime_properties(
            'link_id', target.get_attribute('network_id'))


@utils.operation
async def unlink(source, target, inputs):
    source.context.logger.info(
        '[{0} --X--> {1}] - Network "{2}" detached.'
        .format(target.name,
                source.name,
                target.get_attribute('network_id')))
    for attr in ['link_id', 'subnet_id']:
        if attr in source.runtime_properties:
            del source.runtime_properties[attr]
