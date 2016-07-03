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
from openstack_plugin.networking import port


@utils.operation
async def port_create(node, inputs):
    if 'link_id' not in node.runtime_properties:
        raise Exception('Unable to create port for node "{0}". '
                        'It is necessary to use relationship '
                        'to link port to a network'
                        .format(node.name))

    node.context.logger.info(
        '[{0}] - Attempting to create port.'.format(node.name))

    neutron = clients.openstack.neutron(node)
    port_name = node.properties.get('port_name')
    port_id = node.properties.get('port_id')
    link_id = node.runtime_properties.get('link_id')
    ip_address = node.properties.get('ip_address')
    order = node.properties.get('order')
    is_default = node.properties.get('is_default')
    ip_range_start = node.properties.get('ip_range_start')
    ip_range_end = node.properties.get('ip_range_end')
    admit_state_up = True
    subnet_id = node.runtime_properties.get('subnet_id')
    security_groups = node.runtime_properties.get('security_groups')
    use_existing = True if port_id else False

    identifier = port_name if not port_id else port_id

    _port = await port.create(node.context,
                              identifier, neutron,
                              link_id,
                              subnet_id=subnet_id,
                              ip_addresses=ip_address,
                              admin_state_up=admit_state_up,
                              security_groups=security_groups,
                              use_existing=use_existing)

    node.batch_update_runtime_properties(**{
        'link_id': link_id,
        'port_name': _port['name'],
        'port_id': _port['id'],
        'ip_addresses': ip_address,
        'order': order,
        'is_default': is_default,
        'ip_range_start': ip_range_start,
        'ip_range_end': ip_range_end,
        'mac_address': _port['mac_address'],
        'allowed_address_pairs': _port['allowed_address_pairs'],
    })
    if _port['fixed_ips']:
        fixed_ips = _port['fixed_ips'].pop()
        node.batch_update_runtime_properties(**fixed_ips)

    node.context.logger.info(
        '[{0}] - Port created.'.format(node.name))


@utils.operation
async def port_start(node, inputs):
    node.context.logger.info(
        '[{0}] - Attempting to start port.'
        .format(node.name))
    compute_id = node.runtime_properties.get('compute_id')
    if compute_id:
        port_id = node.runtime_properties['port_id']
        node.context.logger.info(
            '[{0}] - Attempting to attach port "{1}" to '
            'compute node "{2}".'
            .format(node.name, port_id, compute_id))
        nova = clients.openstack.nova(node)
        nova.servers.interface_attach(compute_id, port_id,
                                      None, None)
        node.context.logger.info(
            '[{0}] - Port "{1}" attached.'
            .format(node.name, port_id))
    node.context.logger.info(
        '[{0}] - Port started.'.format(node.name))


@utils.operation
async def port_stop(node, inputs):
    node.context.logger.info(
        '[{0}] - Attempting to stop port.'
        .format(node.name))
    compute_id = node.runtime_properties.get('compute_id')
    if compute_id:
        port_id = node.runtime_properties['port_id']
        node.context.logger.info(
            '[{0}] - Attempting to detach port "{1}" from '
            'compute node "{2}".'
            .format(node.name, port_id, compute_id))
        nova = clients.openstack.nova(node)
        nova.servers.interface_detach(compute_id, port_id)
        node.context.logger.info(
            '[{0}] - Port "{1}" detached.'
            .format(node.name, port_id))
    node.context.logger.info(
        '[{0}] - Port stopped.'.format(node.name))


@utils.operation
async def port_delete(node, inputs):
    task_retries = inputs.get('task_retries', 10)
    task_retry_interval = inputs.get('task_retry_interval', 10)
    neutron = clients.openstack.neutron(node)
    use_existing = True if node.properties.get(
        'port_id') else False
    port_id = node.runtime_properties['port_id']

    await port.delete(node.context, port_id, neutron,
                      use_existing=use_existing,
                      task_retry_interval=task_retry_interval,
                      task_retries=task_retries)


@utils.operation
async def bind_compute_to_port(source, target, inputs):
    source.context.logger.info('[{0} -----> {1}] - Connecting '
                               'compute to port.'
                               .format(target.name, source.name))
    compute_id = target.runtime_properties['server']['id']
    source.update_runtime_properties('compute_id', compute_id)


@utils.operation
async def unbind_compute_from_port(source, target, inputs):
    source.context.logger.info('[{0} --X--> {1}] - Disconnecting '
                               'compute to port.'.format(target.name,
                                                         source.name))
    if 'compute_id' in source.runtime_properties:
        del source.runtime_properties['compute_id']


@utils.operation
async def add_port(source, target, inputs):
    source.context.logger.info(
        '[{0} -----> {1}] - Binding port to compute'
        .format(target.name, source.name))
    nics = source.runtime_properties.get('nics', [])
    _port = {}
    port_id = target.runtime_properties.get('port_id')
    link_id = target.runtime_properties.get('link_id')
    ip_version = target.runtime_properties.get('ip_version')
    ip_address = target.runtime_properties.get('ip_address')

    _port.update({
        'net-id': link_id,
        'port-id': port_id,
        'v{0}-fixed-ip'.format(ip_version):
            ip_address
    })
    nics.append(_port)
    source.update_runtime_properties('nics', nics)


@utils.operation
async def remove_port(source, target, inputs):
    port_id = target.runtime_properties.get('port_id')
    source.context.logger.info(
        '[{0} --X--> {1}] - Unbinding port "{2}" from compute'
        .format(target.name, source.name, port_id))
    if 'nics' in source.runtime_properties:
        del source.runtime_properties['nics']
