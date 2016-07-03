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


async def create(context, name_or_id,
                 neutronclient,
                 network_id,
                 subnet_id=None,
                 ip_addresses=None,
                 admin_state_up=True,
                 security_groups=None,
                 use_existing=False):
    """
    Creates port for specific subnet of network
    :param context:
    :param name_or_id:
    :param neutronclient:
    :param network_id:
    :param subnet_id:
    :param ip_addresses:
    :param admin_state_up:
    :param security_groups:
    :param use_existing:
    :return:
    """

    if not use_existing:
        port_dict = {
            'port': {
                'admin_state_up': admin_state_up,
                'name': name_or_id,
                'network_id': network_id,
            }
        }
        fixed_ips = []
        if subnet_id:
            subnet = {'subnet_id': subnet_id}
            if ip_addresses:
                subnet.update({'ip_address': ip_addresses})
            fixed_ips.append(subnet)
            port_dict['port']['fixed_ips'] = fixed_ips
        if security_groups:
            port_dict['port']['security_groups'] = security_groups

        context.logger.info('Creating port with identifiers: {0}'
                            .format(str(port_dict)))
        port = neutronclient.create_port(body=port_dict)

    else:
        context.logger.info('Using existing port "{0}".'
                            .format(name_or_id))
        port = neutronclient.show_port(name_or_id)

    return port['port']


async def delete(context, name_or_id, neutronclient,
                 use_existing=False,
                 task_retry_interval=None,
                 task_retries=None):
    """
    Deletes port for specific subnet of network
    :param context:
    :param name_or_id:
    :param neutronclient:
    :param use_existing:
    :param task_retry_interval:
    :param task_retries:
    :return:
    """
    if use_existing:
        context.logger.info(
            'Leaving port "{0}" as is, '
            'because of it is external resource.'
            .format(name_or_id))
        return

    neutronclient.delete_port(name_or_id)

    async def is_gone():
        try:
            neutronclient.show_port(name_or_id)
            return False
        except Exception as ex:
            context.logger.debug(str(ex))
            return True

    await utils.retry(is_gone, exceptions=(Exception,),
                      task_retries=task_retries,
                      task_retry_interval=task_retry_interval)
