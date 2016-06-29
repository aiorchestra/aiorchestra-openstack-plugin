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


async def create(context,
                 neutronclient, floating_network_id,
                 port_id, use_existing=False,
                 existing_floating_ip_id=None):
    """

    :param context:
    :param neutronclient:
    :param floating_ip_network:
    :param port_id:
    :param use_existing:
    :param existing_floating_ip_id:
    :return:
    """
    if not use_existing:
        floating_ip_dict = {
            'floating_network_id': floating_network_id,
        }

        if not floating_network_id:
            raise Exception('Network required for floating '
                            'IP provisioning.')
        if port_id:
            context.logger.info(
                'Attempting to create floating '
                'IP for port "{0}".'.format(port_id))
            port = {'port_id': port_id}
            floating_ip_dict.update(port)
        fip = neutronclient.create_floatingip(body={
            'floatingip': floating_ip_dict})
    else:
        fip = neutronclient.show_floatingip(existing_floating_ip_id)

    return fip['floatingip']


async def delete(context, neutronclient,
                 existing_floating_ip_id, use_existing=False):
    """

    :param context:
    :param neutronclient:
    :param existing_floating_ip_id:
    :param use_existing:
    :return:
    """
    if use_existing:
        context.logger.info('Leaving floating IP as is because '
                            'it is an external resource.')
        return

    neutronclient.delete_floatingip(existing_floating_ip_id)

    context.logger.info(
        'Floating IP "{0}" deleted.'.format(existing_floating_ip_id))
