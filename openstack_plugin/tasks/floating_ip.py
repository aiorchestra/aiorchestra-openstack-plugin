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
from openstack_plugin.networking import floating_ip


@utils.operation
async def floatingip_create(node, inputs):
    node.context.logger.info(
        '[{0}] - Attempting to create floating IP.'
        .format(node.name))
    existing_floating_ip_id = node.properties.get(
        'floating_ip_id')
    use_existing = True if existing_floating_ip_id else False

    neutron = clients.openstack.neutron(node)

    port_id = node.runtime_properties.get('port_id')

    floating_network_id = node.runtime_properties.get(
        'floating_network_id')

    fip = await floating_ip.create(
        node.context, neutron, floating_network_id,
        port_id, use_existing=use_existing,
        existing_floating_ip_id=existing_floating_ip_id)

    node.batch_update_runtime_properties(**{
        'floating_ip_id': fip['id'],
    })
    node.batch_update_runtime_properties(**fip)
    node.context.logger.info(
        '[{0}] - Floating IP created.' .format(node.name))


@utils.operation
async def floatingip_delete(node, inputs):
    node.context.logger.info(
        '[{0}] - Attempting to delete floating IP.'.format(node.name))
    fip = node.get_attribute('floating_ip_id')
    use_existing = True if node.properties.get(
        'floating_ip_id') else False
    neutron = clients.openstack.neutron(node)

    await floating_ip.delete(node.context, neutron,
                             fip, use_existing=use_existing)


@utils.operation
async def link_floatingip_to_network(source, target, inputs):
    network_id = target.get_attribute('network_id')
    source.context.logger.info(
        '[{0} -----> {1}] - Connecting floating IP to '
        'network "{2}".'.format(target.name,
                                source.name,
                                network_id))
    source.update_runtime_properties(
        'floating_network_id', network_id)


@utils.operation
async def unlink_floatingip_from_network(source, target, inputs):
    if 'floating_network_id' in source.runtime_properties:
        source.context.logger.info(
            '[{0} --X--> {1}] - Disconnecting floating IP from '
            'network "{2}".'.format(
                    target.name,
                    source.name,
                    source.runtime_properties['floating_network_id']))
        del source.runtime_properties['floating_network_id']


@utils.operation
async def link_floatingip_to_port(source, target, inputs):
    source.update_runtime_properties(
        'port_id', target.runtime_properties.get('port_id'))
    source.context.logger.info(
        '[{0} -----> {1}] - Connecting floating IP to '
        'port "{2}".'.format(target.name,
                             source.name,
                             target.runtime_properties.get('port_id')))


@utils.operation
async def unlink_floatingip_from_port(source, target, inputs):
    if 'port_id' in source.runtime_properties:
        source.context.logger.info(
            '[{0} --X--> {1}] - Disconnecting floating IP from '
            'port "{2}".'.format(target.name,
                                 source.name,
                                 target.runtime_properties.get('port_id')))
        del source.runtime_properties['port_id']


@utils.operation
async def inject_floating_ip_attributes(source, target, inputs):
    source.context.logger.info('[{0} -----> {1}] - Supplying '
                               'floating IP details.'
                               .format(target.name, source.name))
    fip = target.runtime_properties['floating_ip_address']
    source.batch_update_runtime_properties(**{
        'access_ip': fip,
    })


@utils.operation
async def eject_floating_ip_attributes(source, target, inputs):
    source.context.logger.info('[{0} --X--> {1}] - Revoking '
                               'floating IP details.'
                               .format(target.name, source.name))
    for attr in ['access_ip']:
        if attr in source.runtime_properties:
            del source.runtime_properties[attr]
