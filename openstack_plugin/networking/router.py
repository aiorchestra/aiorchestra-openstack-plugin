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


async def create(context, name_or_id, neutronclient,
                 external_gateway_info=None,
                 use_existing=False):
    """
    Creates router
    :param context:
    :param name_or_id:
    :param neutronclient:
    :param external_gateway_info:
    :param use_existing:
    :return:
    """
    if not use_existing:
        context.logger.info(
            'Attempting to create new router "{0}".'
            .format(name_or_id))
        router_dict = {
            'router': {
                'name': name_or_id,
            }
        }
        if external_gateway_info:
            router_dict['router'].update(external_gateway_info)
        router = neutronclient.create_router(router_dict)
    else:
        context.logger.info('Using existing router "{0}".'
                            .format(name_or_id))
        router = neutronclient.show_router(name_or_id)

    return router['router']


async def delete(context, name_or_id, neutronclient,
                 use_existing=False,
                 task_retries=None,
                 task_retry_interval=None):
    """

    :param context:
    :param name_or_id:
    :param neutronclient:
    :param use_existing:
    :param task_retries:
    :param task_retry_interval:
    :return:
    """
    if use_existing:
        context.logger.info('Leaving router "{0}" as is, '
                            'because of it is external resource.'
                            .format(name_or_id))
        return

    context.logger.info(
        'Attempting to delete router "{0}".'
        .format(name_or_id))
    neutronclient.delete_router(name_or_id)

    async def is_gone():
        try:
            neutronclient.show_router(name_or_id)
            return False
        except Exception as ex:
            context.logger.debug(str(ex))
            return True

    await utils.retry(is_gone, exceptions=(Exception,),
                      task_retry_interval=task_retry_interval,
                      task_retries=task_retries)
