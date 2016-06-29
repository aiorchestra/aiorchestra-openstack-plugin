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
from openstack_plugin.networking import subnet
from openstack_plugin.networking import port
from openstack_plugin.networking import router
from openstack_plugin.networking import floating_ip
from openstack_plugin.networking import security_group_and_rules


@utils.operation
async def network_create(node, inputs):
    node.context.logger.info(
        '[{0}] - Attempting to create network.'.format(node.name))
    neutron = clients.openstack.neutron(node)

    net = await network.create(
        node.context,
        node.properties['name_or_id'],
        neutron,
        is_external=node.properties['is_external'],
        admin_state_up=True,
        use_existing=node.properties['use_existing'],
    )

    node.batch_update_runtime_properties(**net)
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
    await network.delete(
        node.context,
        node.get_attribute('id'),
        neutron,
        use_existing=node.properties['use_existing'],
        task_retries=task_retries,
        task_retry_interval=task_retry_interval
    )

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
    node.context.logger.info(
        '[{0}] - Attempting to create subnet "{1}" for network "{2}".'
        .format(node.name, node.properties['name_or_id'],
                node.runtime_properties['network_id']))
    neutron = clients.openstack.neutron(node)

    network_id = node.runtime_properties.get('network_id')
    name_or_id = node.properties.get('name_or_id')
    ip_version = node.properties.get('ip_version')
    cidr = node.properties.get('cidr')
    allocation_pools = node.properties.get('allocation_pools')
    dns_nameservers = node.properties.get('dns_nameservers')
    router_id = node.runtime_properties.get('router_id')
    use_existing = node.properties['use_existing']

    _subnet = await subnet.create(
        node.context,
        name_or_id,
        neutron,
        network_id,
        ip_version,
        cidr,
        allocation_pools,
        dns_nameservers,
        router_id=router_id,
        use_existing=use_existing
    )

    node.batch_update_runtime_properties(**_subnet)
    node.context.logger.info(
        '[{0}] - Subnet "{1}" for network "{2}" was created.'
        .format(node.name,
                _subnet['id'],
                node.runtime_properties['network_id']))


@utils.operation
async def subnet_delete(node, inputs):
    task_retries = inputs.get('task_retries', 10)
    task_retry_interval = inputs.get('task_retry_interval', 10)
    node.context.logger.info('[{0}] - Attempting to delete subnet "{1}".'
                             .format(node.name,
                                     node.properties['name_or_id']))
    neutron = clients.openstack.neutron(node)
    router_id = node.runtime_properties.get('router_id')
    use_existing = node.properties['use_existing']
    name_or_id = node.get_attribute('id')

    await subnet.delete(node.context, name_or_id, neutron,
                        router_id=router_id,
                        use_existing=use_existing,
                        task_retry_interval=task_retry_interval,
                        task_retries=task_retries)


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


@utils.operation
async def port_create(node, inputs):

    node.context.logger.info(
        '[{0}] - Attempting to create subnet port.'
        .format(node.name))

    neutron = clients.openstack.neutron(node)
    name_or_id = node.properties['name_or_id']
    network_id = node.runtime_properties.get('network_id')
    admit_state_up = True
    subnet_id = node.runtime_properties.get('subnet_id')
    security_groups = node.runtime_properties.get('security_groups')
    use_existing = node.properties['use_existing']

    _port = await port.create(node.context, name_or_id, neutron,
                              network_id, subnet_id,
                              admin_state_up=admit_state_up,
                              security_groups=security_groups,
                              use_existing=use_existing)

    fixed_ips = _port['fixed_ips'].pop()
    node.batch_update_runtime_properties(**fixed_ips)

    node.batch_update_runtime_properties(**_port)
    node.context.logger.info(
        '[{0}] - Port created for subnet "{1}".'
        .format(node.name, node.runtime_properties['subnet_id']))


@utils.operation
async def port_delete(node, inputs):
    task_retries = inputs.get('task_retries', 10)
    task_retry_interval = inputs.get('task_retry_interval', 10)
    neutron = clients.openstack.neutron(node)
    use_existing = node.properties['use_existing']
    name_or_id = node.get_attribute('id')

    await port.delete(node.context, name_or_id, neutron,
                      use_existing=use_existing,
                      task_retry_interval=task_retry_interval,
                      task_retries=task_retries)


@utils.operation
async def link_port(source, target, inputs):
    source.context.logger.info(
        '[{0}] - Allowing port "{1}" node to '
        'be attached to subnet "{2}" node.'
        .format(source.name,
                source.properties['name_or_id'],
                target.runtime_properties['id']))
    source.update_runtime_properties(
        'network_id', target.get_attribute('network_id'))
    source.update_runtime_properties(
        'subnet_id',  target.get_attribute('id'))


@utils.operation
async def unlink_port(source, target, inputs):
    source.context.logger.info(
        '[{0}] - Breaking link from port "{1}" node from '
        'subnet "{2}" node.'
        .format(source.name,
                source.properties['name_or_id'],
                target.runtime_properties['id']))
    for attr in ['network_id', 'subnet_id']:
        if attr in source.runtime_properties:
            del source.runtime_properties[attr]


@utils.operation
async def router_create(node, inputs):
    node.context.logger.info('[{0}] - Attempting to create router.'
                             .format(node.name))
    neutron = clients.openstack.neutron(node)

    name_or_id = node.properties['name_or_id']
    use_existing = node.properties['use_existing']
    external_gateway_info = node.runtime_properties.get(
        'external_gateway_info', {})

    _router = await router.create(
        node.context, name_or_id, neutron,
        external_gateway_info=external_gateway_info,
        use_existing=use_existing)

    node.batch_update_runtime_properties(**_router)
    node.context.logger.info(
        '[{0}] - Router "{1}" created.'
        .format(node.name, name_or_id))


@utils.operation
async def router_start(node, inputs):
    _id = node.get_attribute('id')
    neutron = clients.openstack.neutron(node)
    router = neutron.show_router(_id)['router']
    node.batch_update_runtime_properties(**router)
    node.context.logger.info('[{0}] - Router started.'
                             .format(node.name))


@utils.operation
async def router_delete(node, inputs):
    task_retries = inputs.get('task_retries', 10)
    task_retry_interval = inputs.get('task_retry_interval', 10)
    neutron = clients.openstack.neutron(node)
    name_or_id = node.get_attribute('id')
    use_existing = node.properties['use_existing']
    node.context.logger.info(
        '[{0}] - Attempting to delete router "{0}".'
        .format(node.name, name_or_id))

    await router.delete(node.context, name_or_id, neutron,
                        use_existing=use_existing,
                        task_retry_interval=task_retry_interval,
                        task_retries=task_retries)

    node.context.logger.info('[{0}] - Router deleted.'
                             .format(node.name))


@utils.operation
async def link_subnet_to_router(source, target, inputs):
    router_id = target.get_attribute('id')
    source.update_runtime_properties('router_node', target)
    source.update_runtime_properties('router_id', router_id)


@utils.operation
async def unlink_subnet_to_router(source, target, inputs):
    for attr in ['router_node', 'router_id']:
        if attr in source.runtime_properties:
            del source.runtime_properties[attr]


@utils.operation
async def link_router_to_external_network(source, target, inputs):
    source.update_runtime_properties('external_gateway_info', {
        'external_gateway_info': {
            'network_id': target.properties['name_or_id']
        }
    })


@utils.operation
async def unlink_router_from_external_network(source, target, inputs):
    if 'external_gateway_info' in source.runtime_properties:
        del source.runtime_properties['external_gateway_info']


@utils.operation
async def add_port(source, target, inputs):
    nics = source.runtime_properties.get('nics', [])
    _port = {}
    neutron = clients.openstack.neutron(target)
    subnet = neutron.show_subnet(
        target.runtime_properties['subnet_id'])['subnet']
    ip_version = subnet['ip_version']

    _port.update({
        'net-id': target.runtime_properties['network_id'],
        'port-id': target.get_attribute('id'),
        'v{0}-fixed-ip'.format(str(ip_version)):
            target.get_attribute('ip_address')
    })
    nics.append(_port)
    source.update_runtime_properties('nics', nics)


@utils.operation
async def remove_port(source, target, inputs):
    if 'nics' in source.runtime_properties:
        del source.runtime_properties['nics']


@utils.operation
async def floatingip_create(node, inputs):
    node.context.logger.info(
        '[{0}] - Attempting to create floating IP.'
        .format(node.name))
    existing_floating_ip_id = node.properties.get(
        'existing_floating_ip_id')
    use_existing = node.properties['use_existing']
    neutron = clients.openstack.neutron(node)
    port_id = node.runtime_properties.get('port_id')
    floating_network_id = node.runtime_properties.get(
        'floating_network_id')

    fip = await floating_ip.create(
        node.context, neutron, floating_network_id,
        port_id, use_existing=use_existing,
        existing_floating_ip_id=existing_floating_ip_id)

    node.batch_update_runtime_properties(**fip)
    node.context.logger.info(
        '[{0}] - Floating IP created.' .format(node.name))


@utils.operation
async def floatingip_delete(node, inputs):
    node.context.logger.info(
        '[{0}] - Attempting to delete floating IP.'.format(node.name))
    fip = node.runtime_properties['id']
    use_existing = node.properties['use_existing']
    neutron = clients.openstack.neutron(node)

    await floating_ip.delete(node.context, neutron,
                             fip, use_existing=use_existing)


@utils.operation
async def link_floatingip_to_network(source, target, inputs):
    log = source.context.logger
    network_id = target.get_attribute('id')
    log.info('[{0} -----> {1}] - Connecting floating IP to '
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
    log = source.context.logger
    source.update_runtime_properties(
        'port_id', target.get_attribute('id'))
    log.info('[{0} -----> {1}] - Connecting floating IP to '
             'port "{2}".'.format(target.name,
                                  source.name,
                                  target.get_attribute('id')))


@utils.operation
async def unlink_floatingip_from_port(source, target, inputs):
    log = source.context.logger
    if 'port_id' in source.runtime_properties:
        log.info('[{0} --X--> {1}] - Disconnecting floating IP from '
                 'port "{2}".'.format(target.name,
                                      source.name,
                                      target.get_attribute('id')))
        del source.runtime_properties['port_id']


@utils.operation
async def security_group_create(node, inputs):
    log = node.context.logger
    neutron = clients.openstack.neutron(node)
    name_or_id = node.properties['name_or_id']
    use_existing = node.properties['use_existing']
    description = node.properties.get('description')
    rules = node.runtime_properties.get('security_group_rules', [])
    log.info('[{0}] - Attempting to create security group.'
             .format(node.name))
    sg = await security_group_and_rules.create(
        node.context, name_or_id, neutron,
        description=description, use_existing=use_existing)

    node.batch_update_runtime_properties(**sg)
    _rs = [list(r.values()).pop() for r in rules]

    await security_group_and_rules.create_rules(
        node.context, sg['id'], _rs, neutron)

    sg = neutron.show_security_group(sg['id'])

    node.batch_update_runtime_properties(**sg)


@utils.operation
async def security_group_delete(node, inputs):
    neutron = clients.openstack.neutron(node)
    name_or_id = node.get_attribute('id')
    use_existing = node.properties['use_existing']

    await security_group_and_rules.delete(node.context, name_or_id,
                                          neutron, use_existing=use_existing)


@utils.operation
async def connect_security_groups_rule(source, target, inputs):
    source.context.logger.info('[{0} -----> {1}] - Connecting security group '
                               'rule to security group.'
                               .format(target.name, source.name))
    rule = target.properties
    rules = source.runtime_properties.get('security_group_rules', [])
    rules.append({target.name: rule})
    source.update_runtime_properties('security_group_rules', rules)


@utils.operation
async def disconnect_security_groups_rule(source, target, inputs):
    source.context.logger.info('[{0} --X--> {1}] - '
                               'Disconnecting security group '
                               'rule from security group.'
                               .format(target.name, source.name))
    rules = source.runtime_properties.get(
            'security_group_rules', [])
    for name_and_rule in rules:
        if target.name == list(name_and_rule.keys()).pop():
            del name_and_rule[rules.index(name_and_rule)]


@utils.operation
async def link_security_groups_to_port(source, target, inputs):
    sgs = source.runtime_properties.get('security_groups', [])
    sec_id = target.get_attribute('id')
    sgs.append(sec_id)
    source.update_runtime_properties('security_groups', sgs)


@utils.operation
async def unlink_security_groups_from_port(source, target, inputs):
    if 'security_groups' in source.runtime_properties:
        del source.runtime_properties['security_groups']


@utils.operation
async def inject_floating_ip_attributes(source, target, inputs):
    fip = target.runtime_properties['floating_ip_address']
    source.batch_update_runtime_properties(**{
        'access_ip': fip,
    })


@utils.operation
async def eject_floating_ip_attributes(source, target, inputs):
    for attr in ['access_ip']:
        if attr in source.runtime_properties:
            del source.runtime_properties[attr]
