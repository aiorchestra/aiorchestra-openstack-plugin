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

from openstack_plugin.common import clients

from aiorchestra.core import utils

COMPUTE_ACTIVE = 'ACTIVE'
COMPUTE_BUILD = 'BUILD'
COMPUTE_SHUTOFF = 'SHUTOFF'

SERVER_TASK_STATE_POWERING_ON = 'powering-on'


@utils.operation
async def create(node, inputs):
    node.context.logger.info('[{0}] - Attempting to create '
                             'compute instance.'.format(node.name))
    nova = clients.openstack.nova(node)
    name, flavor, image = (
        node.properties['name_or_id'],
        node.properties['flavor'],
        node.properties['image'],
    )
    # node_pool_size = node.properties['node_pool_size']
    if not node.properties['use_existing']:
        try:
            glance = clients.openstack.glance(node)
            glance.images.get(image)
            node.context.logger.info('[{0}] - Image "{1}" exists.'
                                     .format(node.name, image))
            nova.flavors.get(flavor)
            node.context.logger.info('[{0}] - Flavor "{1}" exists.'
                                     .format(node.name, flavor))
        except Exception as ex:
            node.context.logger.error(str(ex))
            raise ex

        try:
            ssh_key = None
            nics = None
            if 'ssh_keypair' in node.runtime_properties:
                ssh_key = node.runtime_properties['ssh_keypair']['name']
            if 'nics' in node.runtime_properties:
                nics = node.runtime_properties['nics']

            server = nova.servers.create(name, image, flavor,
                                         key_name=ssh_key,
                                         nics=nics)
            node.context.logger.info("[{0}] - Compute instance created."
                                     .format(node.name))
        except Exception as ex:
            node.context.logger.error(str(ex))
            raise ex
    else:
        node.context.logger.info('[{0}] - Using existing compute instance.'
                                 .format(node.name))
        server = nova.servers.get(node.properties['name_or_id'])

    node.batch_update_runtime_properties(**{
        'id': server.id,
        'server': server.__dict__,
        'status': server.status,
    })


@utils.operation
async def start(node, inputs):
    task_retries = inputs.get('task_retries', 10)
    task_retry_interval = inputs.get('task_retry_interval', 10)
    nova = clients.openstack.nova(node)
    if not node.properties['use_existing']:
        async def wait_until_active():
            _server = nova.servers.get(node.runtime_properties['server']['id'])
            server_task_state = getattr(_server, 'OS-EXT-STS:task_state')
            if _server.status == COMPUTE_ACTIVE:
                return True

            if _server.status == COMPUTE_BUILD:
                return False

            if (_server.status == COMPUTE_BUILD and
                    server_task_state != SERVER_TASK_STATE_POWERING_ON):
                _server.start()
                return False

            if (_server.status == COMPUTE_BUILD or
                    server_task_state == SERVER_TASK_STATE_POWERING_ON):
                return False
        node.context.logger.info('[{0}] - Starting status polling for '
                                 'compute instance.'.format(node.name))
        await utils.retry(wait_until_active, exceptions=(Exception, ),
                          task_retries=task_retries,
                          task_retry_interval=task_retry_interval)
        node.update_runtime_properties('status', nova.servers.get(
            node.runtime_properties['id']).status)
        _server = nova.servers.get(
            node.runtime_properties['id'])
        node.update_runtime_properties('server', _server.__dict__)
        node.context.logger.info('[{0}] - Compute instance is active.'
                                 .format(node.name))
    else:
        _server = nova.servers.get(node.properties['name_or_id'])
        node.context.logger.info('[{0}] - Compute instance is {1}.'
                                 .format(node.name, _server.status))


@utils.operation
async def delete(node, inputs):
    node.context.logger.info('[{0}] - Attempting to delete compute '
                             'instance.'.format(node.name))
    task_retries = inputs.get('task_retries', 10)
    task_retry_interval = inputs.get('task_retry_interval', 10)
    if not node.properties['use_existing']:
        nova = clients.openstack.nova(node)
        _server = nova.servers.get(
            node.runtime_properties['id'])
        try:
            _server.delete()
        except Exception as ex:
            node.context.logger.debug(str(ex))
            # we don't really care if instance was stopped or not,
            # next operation will delete it
            pass

        async def is_gone():
            try:
                nova.servers.get(
                    node.runtime_properties['id'])
                return False
            except Exception as ex:
                node.context.logger.debug(str(ex))
                return True

        await utils.retry(is_gone, exceptions=(Exception,),
                          task_retries=task_retries,
                          task_retry_interval=task_retry_interval)
        node.context.logger.info('[{0}] - Compute instance deleted.'
                                 .format(node.name))
    else:
        node.context.logger.info('[{0}] - Compute instance remains as is, '
                                 'because it is external resource.'
                                 .format(node.name))
    for attr in ['id', 'server', 'status']:
        if attr in node.runtime_properties:
            del node.runtime_properties[attr]


@utils.operation
async def stop(node, inputs):
    task_retries = inputs.get('task_retries', 10)
    task_retry_interval = inputs.get('task_retry_interval', 10)
    nova = clients.openstack.nova(node)
    if not node.properties['use_existing']:
        node.context.logger.info('[{0}] - Attempting to stop compute '
                                 'instance.'.format(node.name))
        try:
            _server = nova.servers.get(
                node.runtime_properties['id'])
            _server.stop()
        except Exception as ex:
            node.context.logger.debug(str(ex))
            # we don't really care if instance was stopped or not,
            # next operation will delete it
            pass

        async def wait_until_task_finished():
            _server = nova.servers.get(node.runtime_properties['id'])
            server_task_state = getattr(_server, 'OS-EXT-STS:task_state')
            return server_task_state is None

        await utils.retry(wait_until_task_finished, exceptions=(Exception, ),
                          task_retry_interval=task_retry_interval,
                          task_retries=task_retries)
        node.context.logger.info('[{0}] - Compute instance stopped.'
                                 .format(node.name))
    else:
        node.context.logger.info('[{0}] - Leaving instance as is because it '
                                 'is external resource.'.format(node.name))
