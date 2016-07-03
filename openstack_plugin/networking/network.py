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


async def create(context,
                 name_or_id,
                 neutronclient,
                 is_external=False,
                 admin_state_up=True,
                 use_existing=False):
    """
    Creates network for OpenStack using Neutron API
    :param context: OrchestraContext instance
    :param name_or_id: Neutron name or ID
    :param neutronclient: Authorized Neutron client
    :param is_external: weather if network is external
    :param admin_state_up: network state to assign
    :param use_existing: will use existing network
    :return: network: provisioned network
    :rtype: dict
    """
    if not use_existing:
        network = {'name': name_or_id,
                   'admin_state_up': admin_state_up}
        context.logger.info(
            'Creating new network with identifiers {0}.'
            .format(str(network)))
        net = neutronclient.create_network({'network': network})
    else:
        context.logger.info('Using existing network.')
        net = neutronclient.show_network(name_or_id)
        if is_external:
            context.logger.info(
                'Attempting to get external network details.')
            net_details = net['network']
            if not net_details['router:external']:
                raise Exception(
                    'Network "{0}" is not an external. Details: {1}'
                    .format(net_details['id'], str(net_details)))

    return net['network']


async def delete(context,
                 name_or_id,
                 neutronclient,
                 use_existing=False,
                 task_retries=None,
                 task_retry_interval=None):
    """
    Deletes network for OpenStack using Neutron API
    :param context: OrchestraContext instance
    :param name_or_id: Network name or ID
    :param neutronclient: Authorized Neutron client
    :param use_existing: weather if network exists or not
    :param task_retries: task retries
    :param task_retry_interval: task retry interval
    :return:
    """
    if use_existing:
        context.logger.info('Network "{0}" remains as is, '
                            'because it is an external resource.'
                            .format(name_or_id))
        return

    if not use_existing:
        neutronclient.delete_network(name_or_id)

        async def is_gone():
            try:
                neutronclient.show_network(name_or_id)
                return False
            except Exception as ex:
                context.logger.debug(str(ex))
                return True

        await utils.retry(is_gone, exceptions=(Exception, ),
                          task_retries=task_retries,
                          task_retry_interval=task_retry_interval)
