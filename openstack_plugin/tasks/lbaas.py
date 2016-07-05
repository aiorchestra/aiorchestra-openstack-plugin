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


def collect_member_net_attribute(members, attr):
    attrs = []
    for member in members:
        interfaces = member.get('member_interfaces')
        for interface in interfaces:
            for fixed_ip in interface.fixed_ips:
                attrs.append(fixed_ip[attr])
    return attrs


@utils.operation
async def create(node, inputs):
    node.context.logger.info('[{0}] - Attempting to create '
                             'load balancer for required members.'
                             .format(node.name))
    client_capability = node.get_capability('client')
    if not client_capability:
        raise Exception('[{0}] - Unable to resolve load balancer '
                        '"client" capability.'.format(node.name))
    subnet_id = client_capability.get('network_id')
    protocol = node.properties.get('protocol')
    algorithm = node.properties.get('algorithm')
    pool_dict = {
        "pool": {
            "admin_state_up": True,
            "description": "pool for load balancer {0}".format(node.name),
            # it may appear that OpenStack does have LBaaS v1
            "lb_algorithm": algorithm,
            "name": node.name,
            "protocol": protocol,
            "subnet_id": subnet_id,
        }
    }
    neutron = clients.openstack.neutron(node)
    try:
        pool = neutron.create_pool(body=pool_dict)['pool']
    except Exception as ex:
        if 'lb_algorithm' in str(ex):
            node.context.logger.warn('[{0}] - Falling back to '
                                     'LBaaS v1.'.format(node.name))
            # it may appear that OpenStack does have LBaaS v1
            del pool_dict['pool']['lb_algorithm']
            pool_dict['pool']['lb_method'] = algorithm
            pool = neutron.create_pool(body=pool_dict)['pool']
        else:
            raise ex
    node.context.logger.info('[{0}] - Creating pool with identifiers: {1}.'
                             .format(node.name, str(pool_dict)))
    node.batch_update_runtime_properties(**pool)
    node.update_runtime_properties('network_id', subnet_id)
    node.context.logger.info('[{0}] - Load balancer created.'
                             .format(node.name))


@utils.operation
async def start(node, inputs):
    node.context.logger.info('[{0}] - Attempting to start '
                             'load balancer for required members.'
                             .format(node.name))
    # wait until pool is in ACTIVE state
    neutron = clients.openstack.neutron(node)
    pool_id = node.runtime_properties['id']
    async def await_for_active_state():
        pool = neutron.show_pool(pool_id)['pool']
        return pool['status'] == 'ACTIVE'

    await utils.retry(await_for_active_state, task_retries=3)

    protocol_port = node.properties.get('protocol_port')
    members = node.runtime_properties.get('pool_members')
    pool_members = []
    for member in members:
        member_dict = {
            'member': {
                'address': member['ip_address'],
                'protocol_port': protocol_port,
                'weight': member['weight'],
                'pool_id': pool_id,
            }
        }
        node.context.logger.info('[{0}] - Adding member to load '
                                 'balancer pool.'.format(node.name))
        member = neutron.create_member(body=member_dict)['member']
        pool_members.append(member)
    node.update_runtime_properties('pool_members', pool_members)
    node.context.logger.info('[{0}] - Load balancer started.'
                             .format(node.name))


@utils.operation
async def stop(node, inputs):
    node.context.logger.info('[{0}] - Attempting to stop '
                             'load balancer for required members.'
                             .format(node.name))
    neutron = clients.openstack.neutron(node)
    for member in node.runtime_properties.get('pool_members', []):
        member_id = member['id']
        neutron.delete_member(member_id)
    node.context.logger.info('[{0}] - Load balancer stopped.'
                             .format(node.name))


@utils.operation
async def delete(node, inputs):
    node.context.logger.info('[{0}] - Attempting to delete '
                             'load balancer for required members.'
                             .format(node.name))
    neutron = clients.openstack.neutron(node)
    pool_id = node.runtime_properties['id']
    neutron.delete_pool(pool_id)
    node.context.logger.info('[{0}] - Load balancer deleted.'
                             .format(node.name))


@utils.operation
async def add_member(source, target, inputs):
    source.context.logger.info('[{0} -----> {1}] - Connecting '
                               'application compute to '
                               'load balancer members.'
                               .format(target.name, source.name))
    member_capability = source.get_requirement_capability(target)
    ip_address = member_capability.get('ip_address')
    weight = member_capability.get('weight')
    members = source.runtime_properties.get('pool_members', [])
    member_dict = {
        'ip_address': ip_address,
        'weight': weight,
    }
    members.append(member_dict)
    source.update_runtime_properties('pool_members', members)


@utils.operation
async def remove_member(source, target, inputs):
    source.context.logger.info('[{0} --X--> {1}] - Disconnecting '
                               'application compute from '
                               'load balancer members.'
                               .format(target.name, source.name))
    if 'pool_members' in source.runtime_properties:
        del source.runtime_properties['pool_members']
