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

COMPUTE_ACTIVE = 'ACTIVE'
COMPUTE_BUILD = 'BUILD'
COMPUTE_SHUTOFF = 'SHUTOFF'

SERVER_TASK_STATE_POWERING_ON = 'powering-on'


async def create(context, novaclient, glanceclient, name_or_id, flavor,
                 image, ssh_keyname=None, nics=None, use_existing=False,
                 files=None, config_drive=False, userdata=None):
    """
    Creates compute instance
    :param context: OrchestraContext
    :param novaclient: Authorized Nova client
    :param glanceclient: Authorized Glance client
    :param name_or_id: Instance name or ID
    :param flavor: Instance flavor
    :param image: Instance image
    :param ssh_keyname: name of SSH keypair to be injected
    :param nics: Neutron port definitions for an instance
    :param use_existing: weather use existing instance or create new
    :param files: dict of file injections
    :param config_drive: use config driver or not
    :return: instance
    """
    if not use_existing:
        glanceclient.images.get(image)
        context.logger.debug('Image "{0}" exists.'
                             .format(image))
        novaclient.flavors.get(flavor)
        context.logger.debug('Flavor "{0}" exists.'
                             .format(flavor))

        instance = novaclient.servers.create(
            name_or_id, image, flavor,
            key_name=ssh_keyname,
            nics=nics, files=files,
            config_drive=config_drive,
            userdata=userdata,
        )
        context.logger.info('Compute instance "{0}" created.'
                            .format(name_or_id))
    else:
        instance = novaclient.servers.get(name_or_id)

    return instance


async def start(context, novaclient, name_or_id,
                use_existing=False,
                task_retry_interval=None,
                task_retries=None):
    """

    :param context:
    :param novaclient:
    :param name_or_id:
    :param use_existing:
    :param task_retry_interval:
    :param task_retries:
    :return:
    """
    if use_existing:
        context.logger.info('Using existing instance in its original state.')
        return

    async def wait_until_active():
        instance = novaclient.servers.get(name_or_id)
        server_task_state = getattr(instance, 'OS-EXT-STS:task_state')
        if instance.status == COMPUTE_ACTIVE:
            return True

        if instance.status == COMPUTE_BUILD:
            return False

        if (instance.status == COMPUTE_BUILD and
                server_task_state != SERVER_TASK_STATE_POWERING_ON):
            instance.start()
            return False

        if (instance.status == COMPUTE_BUILD or
                server_task_state == SERVER_TASK_STATE_POWERING_ON):
            return False

    await utils.retry(wait_until_active, exceptions=(Exception,),
                      task_retries=task_retries,
                      task_retry_interval=task_retry_interval)
    context.logger.info('Compute instance started.'.format(name_or_id))


async def delete(context, novaclient, name_or_id,
                 use_existing=False,
                 task_retry_interval=None,
                 task_retries=None):
    """
    Deletes compute instance
    :param context:
    :param novaclient:
    :param name_or_id:
    :param use_existing:
    :param task_retry_interval:
    :param task_retries:
    :return:
    """
    if use_existing:
        context.logger.info('Compute instance "{0}" remains as is, '
                            'because it is external resource.'
                            .format(name_or_id))
        return

    instance = novaclient.servers.get(name_or_id)
    try:
        instance.delete()
    except Exception as ex:
        context.logger.debug(str(ex))
        # we don't really care if instance was stopped or not,
        # next operation will delete it
        pass

    async def is_gone():
        try:
            novaclient.servers.get(name_or_id)
            return False
        except Exception as ex:
            context.logger.debug(str(ex))
            return True

    await utils.retry(is_gone, exceptions=(Exception,),
                      task_retries=task_retries,
                      task_retry_interval=task_retry_interval)
    context.logger.info('Compute instance "{0}" deleted.'
                        .format(name_or_id))


async def stop(context, novaclient, name_or_id,
               use_existing=False,
               task_retry_interval=None,
               task_retries=None):
    """
    Stops compute instance
    :param context:
    :param novaclient:
    :param name_or_id:
    :param use_existing:
    :param task_retry_interval:
    :param task_retries:
    :return:
    """
    if use_existing:
        context.logger.info('Leaving compute instance "{0}" as is because it '
                            'is external resource.'.format(name_or_id))
        return

    context.logger.info('Attempting to stop compute '
                        'instance "{0}".'.format(name_or_id))
    try:
        instance = novaclient.servers.get(name_or_id)
        instance.stop()
    except Exception as ex:
        context.logger.debug(str(ex))
        # we don't really care if instance was stopped or not,
        # next operation will delete it
        pass

    async def wait_until_task_finished():
        instance = novaclient.servers.get(name_or_id)
        server_task_state = getattr(instance, 'OS-EXT-STS:task_state')
        return server_task_state is None

    await utils.retry(wait_until_task_finished, exceptions=(Exception, ),
                      task_retry_interval=task_retry_interval,
                      task_retries=task_retries)
    context.logger.info('Compute instance "{0}" stopped.'
                        .format(name_or_id))
