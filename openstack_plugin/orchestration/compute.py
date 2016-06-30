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
from openstack_plugin.compute import instances


@utils.operation
async def create(node, inputs):
    node.context.logger.info('[{0}] - Attempting to create '
                             'compute instance.'.format(node.name))
    nova = clients.openstack.nova(node)
    glance = clients.openstack.glance(node)

    (name_or_id, flavor, image, config_drive,
     use_existing, files, ssh_key, nics) = (
        node.properties['name_or_id'],
        node.properties['flavor'],
        node.properties['image'],
        node.properties.get('config_drive'),
        node.properties['use_existing'],
        node.runtime_properties.get('injections', {}),
        node.runtime_properties.get(
            'ssh_keypair', {'name': None})['name'],
        node.runtime_properties.get('nics', None)
    )

    instance = await instances.create(
        node.context, nova, glance,
        name_or_id, flavor, image,
        ssh_keyname=ssh_key, nics=nics,
        config_drive=config_drive,
        use_existing=use_existing,
        files=files,
    )

    node.batch_update_runtime_properties(**{
        'id': instance.id,
        'server': instance.__dict__,
        'status': instance.status,
    })


@utils.operation
async def setup_injection(node, inputs):
    node.context.logger.info('[{0}] - Setting up file injection.'
                             .format(node.name))
    local_file = node.properties['local_file_path']
    remote_file_path = node.properties['remote_file_path']
    with open(local_file, 'r') as injection:
        local_file_content = injection.read()
        node.update_runtime_properties(
            'injection', {remote_file_path: local_file_content})


@utils.operation
async def inject_file(source, target, inputs):
    source.context.logger.info('[{0} -----> {1}] - Injecting file to '
                               'compute instance.'
                               .format(target.name, source.name))
    files = source.runtime_properties.get('injections', {})
    files.update(target.runtime_properties['injection'])
    source.update_runtime_properties('injections', files)


@utils.operation
async def eject_file(source, target, inputs):
    source.context.logger.info('[{0} --X--> {1}] - Ejecting file from '
                               'compute instance.'
                               .format(target.name, source.name))
    if 'injections' in source.runtime_properties:
        del source.runtime_properties['injections']


@utils.operation
async def start(node, inputs):
    task_retries = inputs.get('task_retries', 10)
    task_retry_interval = inputs.get('task_retry_interval', 10)
    nova = clients.openstack.nova(node)
    use_existing = node.properties['use_existing']
    name_or_id = node.runtime_properties['server']['id']

    await instances.start(
        node.context, nova, name_or_id,
        use_existing=use_existing,
        task_retries=task_retries,
        task_retry_interval=task_retry_interval,
    )


@utils.operation
async def delete(node, inputs):
    node.context.logger.info('[{0}] - Attempting to delete compute '
                             'instance.'.format(node.name))
    task_retries = inputs.get('task_retries', 10)
    task_retry_interval = inputs.get('task_retry_interval', 10)
    use_existing = node.properties['use_existing']
    name_or_id = node.runtime_properties['server']['id']
    nova = clients.openstack.nova(node)

    await instances.delete(node.context, nova, name_or_id,
                           use_existing=use_existing,
                           task_retry_interval=task_retry_interval,
                           task_retries=task_retries)

    for attr in ['id', 'server', 'status']:
        if attr in node.runtime_properties:
            del node.runtime_properties[attr]


@utils.operation
async def stop(node, inputs):
    task_retries = inputs.get('task_retries', 10)
    task_retry_interval = inputs.get('task_retry_interval', 10)
    nova = clients.openstack.nova(node)
    use_existing = node.properties['use_existing']
    name_or_id = node.runtime_properties['id']

    await instances.stop(node.context, nova, name_or_id,
                         use_existing=use_existing,
                         task_retries=task_retries,
                         task_retry_interval=task_retry_interval)
