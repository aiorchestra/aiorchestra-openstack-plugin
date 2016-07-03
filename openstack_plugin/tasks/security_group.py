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
from openstack_plugin.networking import security_group_and_rules


@utils.operation
async def security_group_create(node, inputs):
    neutron = clients.openstack.neutron(node)
    sg_name = node.properties.get('security_group_name')
    sg_id = node.properties.get('security_group_id')
    use_existing = True if sg_id else False
    description = node.properties.get(
        'description', 'Security group for node [{0}]'
        .format(node.name))
    rules = node.runtime_properties.get('security_group_rules', [])
    node.context.logger.info(
        '[{0}] - Attempting to create security group.'
        .format(node.name))
    identifier = sg_name if not sg_id else sg_id

    sg = await security_group_and_rules.create(
        node.context, identifier, neutron,
        description=description, use_existing=use_existing)

    node.update_runtime_properties('security_group_id', sg['id'])

    _rs = [list(r.values()).pop() for r in rules]
    await security_group_and_rules.create_rules(
        node.context, sg['id'], _rs, neutron)

    node.context.logger.info(
        '[{0}] - Security group created.'.format(node.name))


@utils.operation
async def security_group_delete(node, inputs):
    node.context.logger.info(
        '[{0}] - Attempting to delete security group.'
        .format(node.name))
    neutron = clients.openstack.neutron(node)
    sg_id = node.get_attribute('security_group_id')
    use_existing = True if node.properties.get(
        'security_group_id') else False

    await security_group_and_rules.delete(
        node.context, sg_id, neutron, use_existing=use_existing)
    node.context.logger.info(
        '[{0}] - Security group deleted.'
        .format(node.name))


@utils.operation
async def connect_security_groups_rule(source, target, inputs):
    source.context.logger.info('[{0} -----> {1}] - '
                               'Connecting security group '
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
    if 'security_group_rules' in source.runtime_properties:
        del source.runtime_properties['security_group_rules']


@utils.operation
async def link_security_groups_to_port(source, target, inputs):
    sgs = source.runtime_properties.get('security_groups', [])
    sec_id = target.get_attribute('security_group_id')
    sgs.append(sec_id)
    source.update_runtime_properties('security_groups', sgs)


@utils.operation
async def unlink_security_groups_from_port(source, target, inputs):
    if 'security_groups' in source.runtime_properties:
        del source.runtime_properties['security_groups']
