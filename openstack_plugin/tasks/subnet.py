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
from openstack_plugin.networking import subnet


# https://wiki.openstack.org/wiki/Neutron/APIv2-specification#Create_Subnet
@utils.operation
async def subnet_create(node, inputs):
    if 'link_id' not in node.runtime_properties:
        raise Exception('Unable to create subnet for node "{0}". '
                        'It is necessary to use relationship '
                        'to link subnet to network.'.format(node.name))

    neutron = clients.openstack.neutron(node)

    link_id = node.runtime_properties['link_id']

    network_id = node.properties.get('network_id')
    network_name = node.properties.get('network_name')
    ip_version = node.properties.get('ip_version')
    cidr = node.properties.get('cidr')
    pool_start_ip = node.properties.get('start_ip')
    pool_end_ip = node.properties.get('end_ip')
    dhcp_enabled = node.properties.get('dhcp_enabled')
    dns_nameservers = node.properties.get('dns_nameservers')

    router_id = node.runtime_properties.get('router_id')

    use_existing = True if network_id else False
    identifier = network_name if not network_id else network_id

    allocation_pools = [
        {
            'start': pool_start_ip,
            'end': pool_end_ip,
        },
    ]

    node.context.logger.info(
        '[{0}] - Attempting to create subnet "{1}" for network "{2}".'
        .format(node.name, network_name, link_id))

    _subnet = await subnet.create(
        node.context,
        identifier,
        neutron,
        link_id,
        ip_version,
        cidr,
        allocation_pools,
        dns_nameservers,
        dhcp_enabled=dhcp_enabled,
        router_id=router_id,
        use_existing=use_existing
    )

    node.batch_update_runtime_properties(**{
        'link_id': link_id,
        'network_id': _subnet['id'],
        'network_name': _subnet['name'],
        'ip_version': ip_version,
        'cidr': cidr,
        'star_ip': pool_start_ip,
        'end_ip': pool_end_ip,
        'enable_dhcp': dhcp_enabled,
        'dns_nameservers': dns_nameservers,
        'gateway_ip': _subnet['gateway_ip'],
        'host_routes': _subnet['host_routes'],
        'router_id': router_id,
    })

    node.context.logger.info(
        '[{0}] - Subnet "{1}" for network "{2}" was created.'
        .format(node.name, identifier, link_id))


@utils.operation
async def subnet_delete(node, inputs):
    task_retries = inputs.get('task_retries', 10)
    task_retry_interval = inputs.get('task_retry_interval', 10)
    node.context.logger.info('[{0}] - Attempting to delete subnet "{1}".'
                             .format(node.name,
                                     node.get_attribute('network_id')))
    neutron = clients.openstack.neutron(node)
    router_id = node.runtime_properties.get('router_id')

    net_id = node.get_attribute('network_id')
    use_existing = True if node.properties.get(
        'network_id') else False

    await subnet.delete(node.context, net_id, neutron,
                        router_id=router_id,
                        use_existing=use_existing,
                        task_retry_interval=task_retry_interval,
                        task_retries=task_retries)


@utils.operation
async def link_subnet_to_router(source, target, inputs):
    source.context.logger.info('[{0} -----> {1}] - Connecting network to '
                               'router "{2}".'
                               .format(target.name,
                                       source.name,
                                       target.get_attribute('router_id')))
    router_id = target.get_attribute('router_id')
    source.update_runtime_properties('router_id', router_id)


@utils.operation
async def unlink_subnet_to_router(source, target, inputs):
    source.context.logger.info('[{0} -----> {1}] - Disconnecting network from '
                               'router "{2}".'
                               .format(target.name,
                                       source.name,
                                       target.get_attribute('router_id')))
    for attr in ['router_id', ]:
        if attr in source.runtime_properties:
            del source.runtime_properties[attr]
