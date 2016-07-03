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
from openstack_plugin.networking import router


@utils.operation
async def router_create(node, inputs):
    node.context.logger.info('[{0}] - Attempting to create router.'
                             .format(node.name))
    neutron = clients.openstack.neutron(node)

    router_name = node.properties.get('router_name')
    router_id = node.properties.get('router_id')
    use_existing = True if router_id else False
    identifier = router_name if not router_id else router_id
    external_gateway_info = node.runtime_properties.get(
        'external_gateway_info', {})

    _router = await router.create(
        node.context, identifier, neutron,
        external_gateway_info=external_gateway_info,
        use_existing=use_existing)

    node.update_runtime_properties('router_id', _router['id'])
    node.context.logger.info(
        '[{0}] - Router "{1}" created.'
        .format(node.name, identifier))


@utils.operation
async def router_start(node, inputs):
    router_id = node.get_attribute('router_id')
    neutron = clients.openstack.neutron(node)
    _router = neutron.show_router(router_id)['router']
    node.batch_update_runtime_properties(**_router)
    node.context.logger.info('[{0}] - Router started.'
                             .format(node.name))


@utils.operation
async def router_delete(node, inputs):
    task_retries = inputs.get('task_retries', 10)
    task_retry_interval = inputs.get('task_retry_interval', 10)
    neutron = clients.openstack.neutron(node)
    router_id = node.get_attribute('router_id')
    use_existing = True if node.properties.get('router_id') else False

    node.context.logger.info(
        '[{0}] - Attempting to delete router "{0}".'
        .format(node.name, router_id))

    await router.delete(node.context, router_id, neutron,
                        use_existing=use_existing,
                        task_retry_interval=task_retry_interval,
                        task_retries=task_retries)

    node.context.logger.info('[{0}] - Router deleted.'
                             .format(node.name))


@utils.operation
async def link_router_to_external_network(source, target, inputs):
    source.context.logger.info('[{0} -----> {1}] - Connecting router to '
                               'external network.'
                               .format(target.name, source.name))
    source.update_runtime_properties('external_gateway_info', {
        'external_gateway_info': {
            'network_id': target.get_attribute('network_id')
        }
    })


@utils.operation
async def unlink_router_from_external_network(source, target, inputs):
    source.context.logger.info('[{0} --X--> {1}] - Disconnecting router from '
                               'external network.'
                               .format(target.name, source.name))
    if 'external_gateway_info' in source.runtime_properties:
        del source.runtime_properties['external_gateway_info']
