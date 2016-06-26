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
        is_external = node.properties['is_external']
        net = neutron.show_network(node.properties['name_or_id'])
        if is_external:
            net_details = net['network']
            if not net_details['router:external']:
                raise Exception('[{0}] - Network "{1}" is not an external.'
                                .format(node.name, net_details['id']))
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

        async def is_gone():
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
    else:
        node.context.logger.info('[{0}] - Network "{1}" remains as is, '
                                 'because it is an external resource'
                                 .format(node.name,
                                         node.attributes['id']))


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
        if 'router_id' in node.runtime_properties:
            router_node = node.runtime_properties['router_node']
            router_id = node.runtime_properties['router_id']
            node.context.logger.info('[{0}] - Attaching subnet "{1}" '
                                     'to router "{2}".'
                                     .format(node.name,
                                             subnet['subnet']['id'],
                                             router_id))
            neutron.add_interface_router(
                router_id, {'subnet_id': subnet['subnet']['id']})
            router = neutron.show_router(router_id)['router']
            router_node.batch_update_runtime_properties(**router)
        subnet = neutron.show_subnet(subnet['subnet']['id'])
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
        subnet = neutron.show_subnet(node.get_attribute('id'))
        if 'router_id' in node.runtime_properties:
            router_node = node.runtime_properties['router_node']
            router_id = node.runtime_properties['router_id']
            node.context.logger.info('[{0}] - Attaching subnet "{1}" '
                                     'to router "{2}".'
                                     .format(node.name,
                                             subnet['subnet']['id'],
                                             router_id))
            neutron.remove_interface_router(
                router_id, {'subnet_id': node.get_attribute('id')})
            router = neutron.show_router(router_id)['router']
            router_node.batch_update_runtime_properties(**router)
        neutron.delete_subnet(node.get_attribute('id'))

        async def is_gone():
            try:
                neutron.show_subnet(node.get_attribute('id'))
                return False
            except Exception as ex:
                node.context.logger.debug(str(ex))
                return True

        await utils.retry(is_gone, exceptions=(Exception,),
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


@utils.operation
async def port_create(node, inputs):
    if 'network_id' not in node.runtime_properties:
        raise Exception('Unable to create subnet for node "{0}". '
                        'It is necessary to use relationship '
                        'to link subnet to network.'.format(node.name))
    neutron = clients.openstack.neutron(node)
    if not node.properties['use_existing']:
        name_or_id = node.properties['name_or_id']
        network_id = node.runtime_properties['network_id']
        admit_state_up = True
        subnet_id = node.runtime_properties['subnet_id']
        node.context.logger.info('[{0}] - Attempting to create port at '
                                 'subnet "{1}" of network "{2}".'
                                 .format(node.name,
                                         subnet_id,
                                         network_id))
        port_dict = {
            'port': {
                'admin_state_up': admit_state_up,
                'name': name_or_id,
                'network_id': network_id,
                'fixed_ips': [
                    {
                        'subnet_id': subnet_id
                    }
                ]

            }
        }

        if 'security_groups' in node.runtime_properties:
            port_dict['port']['security_groups'] = (
                node.runtime_properties['security_groups'])

        port = neutron.create_port(body=port_dict)['port']
        node.context.logger.info(
            '[{0}] - Port at subnet "{1}" of network "{2}".'
            .format(node.name,
                    subnet_id,
                    network_id))
    else:
        node.context.logger.info('[{0}] - Using existing port "{1}".'
                                 .format(node.name,
                                         node.properties['name_or_id']))
        port = neutron.show_port(node.properties['name_or_id'])['port']
    for k, v in port.items():
        if k == 'fixed_ips':
            ip_and_subnet = port[k].pop()
            node.batch_update_runtime_properties(**ip_and_subnet)
    node.batch_update_runtime_properties(**port)
    node.context.logger.info(
        '[{0}] - Port created for subnet "{1}".'
        .format(node.name, node.runtime_properties['subnet_id']))


@utils.operation
async def port_delete(node, inputs):
    task_retries = inputs.get('task_retries', 10)
    task_retry_interval = inputs.get('task_retry_interval', 10)
    neutron = clients.openstack.neutron(node)
    if not node.properties['use_existing']:
        id = node.get_attribute('id')
        neutron.delete_port(id)

        async def is_gone():
            try:
                neutron.show_port(id)
                return False
            except Exception as ex:
                node.context.logger.debug(str(ex))
                return True

        await utils.retry(is_gone, exceptions=(Exception, ),
                          task_retries=task_retries,
                          task_retry_interval=task_retry_interval)
    else:
        node.context.logger.info(
            '[{0}] - Leaving port "{1}" as is, '
            'because of it is external resource.'
            .format(node.name, node.get_attribute('id')))


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
    neutron = clients.openstack.neutron(node)
    name_or_id = node.properties['name_or_id']
    if not node.properties['use_existing']:
        node.context.logger.info(
            '[{0}] - Attempting to create router "{1}".'
            .format(node.name, name_or_id))
        router_dict = {
            'router': {
                'name': name_or_id,
            }
        }
        if 'external_gateway_info' in node.runtime_properties:
            router_dict['router'].update(node.runtime_properties[
                                   'external_gateway_info'])
        router = neutron.create_router(router_dict)['router']
    else:
        node.context.logger.info('[{0}] - Using existing router "{1}".'
                                 .format(node.name, name_or_id))
        router = neutron.show_router(name_or_id)['router']
    node.batch_update_runtime_properties(**router)
    node.context.logger.info(
        '[{0}] - Router "{1}" created.'
        .format(node.name, name_or_id))


@utils.operation
async def router_delete(node, inputs):
    task_retries = inputs.get('task_retries', 10)
    task_retry_interval = inputs.get('task_retry_interval', 10)
    neutron = clients.openstack.neutron(node)
    name_or_id = node.properties['name_or_id']
    if not node.properties['use_existing']:
        node.context.logger.info(
            '[{0}] - Attempting to delete router "{1}".'
            .format(node.name, name_or_id))
        neutron.delete_router(node.get_attribute('id'))

        async def is_gone():
            try:
                neutron.show_router(node.get_attribute('id'))
                return False
            except Exception as ex:
                node.context.logger.debug(str(ex))
                return True

        await utils.retry(is_gone, exceptions=(Exception, ),
                          task_retry_interval=task_retry_interval,
                          task_retries=task_retries)
    else:
        node.context.logger.info('[{0}] - Leaving router "{1}" as is, '
                                 'because of it is external resource.'
                                 .format(node.name, name_or_id))


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
    port = {}
    neutron = clients.openstack.neutron(target)
    subnet = neutron.show_subnet(
        target.runtime_properties['subnet_id'])['subnet']
    ip_version = subnet['ip_version']

    port.update({
        'net-id': target.runtime_properties['network_id'],
        'port-id': target.get_attribute('id'),
        'v{0}-fixed-ip'.format(str(ip_version)):
            target.get_attribute('ip_address')
    })
    nics.append(port)
    source.update_runtime_properties('nics', nics)


@utils.operation
async def remove_port(source, target, inputs):
    if 'nics' in source.runtime_properties:
        del source.runtime_properties['nics']


@utils.operation
async def floatingip_create(node, inputs):
    log = node.context.logger
    if 'floating_network_id' not in node.runtime_properties:
        raise Exception('[{0}] - Network required for floating '
                        'IP provisioning.'.format(node.name))
    floating_ip_dict = {
        'floating_network_id': node.runtime_properties[
            'floating_network_id']
    }
    log.info('[{0}] - Attempting to create floating IP.'
             .format(node.name))
    if 'port_id' in node.runtime_properties:
        log.info('[{0}] - Attempting to create floating IP for port "{1}".'
                 .format(node.name, node.runtime_properties['port_id']))
        port = {'port_id': node.runtime_properties['port_id']}
        floating_ip_dict.update(port)
    neutron = clients.openstack.neutron(node)

    fip = neutron.create_floatingip(body={
        'floatingip': floating_ip_dict})['floatingip']

    node.batch_update_runtime_properties(**fip)
    log.info('[{0}] - Floating IP created.'
             .format(node.name))


@utils.operation
async def floatingip_delete(node, inputs):
    log = node.context.logger
    log.info('[{0}] - Attempting to delete floating IP.'
             .format(node.name))
    fip = node.runtime_properties['id']
    neutron = clients.openstack.neutron(node)
    neutron.delete_floatingip(fip)
    log.info('[{0}] - Floating IP deleted.'
             .format(node.name))


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
    if not node.properties['use_existing']:
        log.info('[{0}] - Attempting to create security group.'
                 .format(node.name))
        description = node.properties.get('description')
        rules = node.properties.get('rules', [])
        sg_dict = {
            'description': description,
            'name': name_or_id,
        }
        sg = neutron.create_security_group(
            {'security_group': sg_dict})['security_group']
        log.info('[{0}] - Security group created.'
                 .format(node.name))
        node.batch_update_runtime_properties(**sg)
        for rule in rules:
            rule.update(security_group_id=sg['id'])
            log.info('[{0}] - Attempting to create rule for '
                     'security group "{1}".'
                     .format(node.name, sg['id']))

            _r = neutron.create_security_group_rule(
                {'security_group_rule': rule}
            )['security_group_rule']

            log.info('[{0}] - Security group rule create: "{1}".'
                     .format(node.name, _r['id']))
        sg = neutron.show_security_group(sg['id'])
    else:
        log.info('[{0}] - Using existing security group.'.format(node.name))
        sg = neutron.show_security_group(name_or_id)['security_group']

    node.batch_update_runtime_properties(**sg)


@utils.operation
async def security_group_delete(node, inputs):
    log = node.context.logger
    neutron = clients.openstack.neutron(node)
    if not node.properties['use_existing']:
        id = node.get_attribute('id')
        neutron.delete_security_group(id)
    else:
        log.info('[{0}] - Security group remains as is, '
                 'because it is an external resource'.format(node.name))


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
