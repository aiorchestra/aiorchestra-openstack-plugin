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
async def network_create(node, inputs):
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
async def network_delete(node, inputs):
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


# https://wiki.openstack.org/wiki/Neutron/APIv2-specification#Create_Subnet
@utils.operation
async def subnet_create(node, inputs):
    if 'network_id' not in node.runtime_properties:
        raise Exception('Unable to create subnet for node "{0}". '
                        'It is necessary to use relationship '
                        'to link subnet to network.'.format(node.name))
    neutron = clients.openstack.neutron(node)
    if not node.properties['use_existing']:
        network_id = node.runtime_properties['network_id']
        name = node.properties['name_or_id']
        ip_version = node.properties['ip_version']
        cidr = node.properties['cidr']
        allocation_pools = node.properties['allocation_pools']
        dns_nameservers = node.properties['dns_nameservers']
        subnet_body = {
            'subnet': {
                'name': name,
                'network_id': network_id,
                'ip_version': ip_version,
                'cidr': cidr,
                'allocation_pools': allocation_pools,
                'dns_nameservers': dns_nameservers,
            }
        }
        subnet = neutron.create_subnet(body=subnet_body)
    else:
        node.context.logger.info('[{0}] - Using existing subnet "{1}".'
                                 .format(node.name,
                                         node.properties['name_or_id']))
        subnet = neutron.show_subnet(node.properties['name_or_id'])

    node.batch_update_runtime_properties(**subnet['subnet'])
    node.context.logger.info(
        '[{0}] - Subnet "{1}" for network "{2}" was created.'
        .format(node.name,
                subnet['subnet']['id'],
                node.runtime_properties['network_id']))


@utils.operation
async def subnet_delete(node, inputs):
    task_retries = inputs.get('task_retries', 10)
    task_retry_interval = inputs.get('task_retry_interval', 10)
    node.context.logger.info('[{0}] - Attempting to delete subnet "{1}".'
                             .format(node.name,
                                     node.properties['name_or_id']))
    neutron = clients.openstack.neutron(node)
    if not node.properties['use_existing']:
        neutron.delete_subnet(node.get_attribute('id'))

        def is_gone():
            try:
                neutron.show_subnet(node.get_attribute('id'))
                return False
            except Exception as ex:
                node.context.logger.debug(str(ex))
                return True
        await utils.retry(is_gone, exceptions=(Exception, ),
                          task_retries=task_retries,
                          task_retry_interval=task_retry_interval)
        node.context.logger.info('[{0}] - Subnet "{1}" deleted.'
                                 .format(node.name,
                                         node.get_attribute('id')))
    else:
        node.context.logger.info('[{0}] - Subnet remains as is, '
                                 'because it is external resource.'
                                 .format(node.name))


@utils.operation
async def link_subnet(source, target, inputs):
    source.context.logger.info(
        '[{0}] - Allowing subnet "{1}" node to '
        'be attached to network "{2}" node.'
        .format(source.name,
                source.properties['name_or_id'],
                target.runtime_properties['id']))
    source.update_runtime_properties(
        'network_id', target.get_attribute('id'))


@utils.operation
async def unlink_subnet(source, target, inputs):
    source.context.logger.info(
        '[{0}] - Breaking link subnet "{1}" node from '
        'network "{2}" node.'
        .format(source.name,
                source.properties['name_or_id'],
                target.runtime_properties['id']))
    if 'network_id' in source.runtime_properties:
        del source.runtime_properties['network_id']
