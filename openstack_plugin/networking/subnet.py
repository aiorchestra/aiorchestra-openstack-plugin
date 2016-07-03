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
                 network_id,
                 ip_version,
                 cidr,
                 allocation_pools,
                 dns_nameservers,
                 dhcp_enabled=True,
                 router_id=None,
                 use_existing=False,):
    """
    Creates subnet for given network
    :param context:
    :param name_or_id:
    :param neutronclient:
    :param network_id:
    :param ip_version:
    :param cidr:
    :param allocation_pools:
    :param dns_nameservers:
    :param dhcp_enabled:
    :param router_id:
    :param use_existing:
    :return:
    """
    if not use_existing:
        subnet_body = {
            'subnet': {
                'name': name_or_id,
                'network_id': network_id,
                'ip_version': ip_version,
                'cidr': cidr,
                'allocation_pools': allocation_pools,
                'dns_nameservers': dns_nameservers,
                'enable_dhcp': dhcp_enabled,
            }
        }
        subnet = neutronclient.create_subnet(body=subnet_body)

    else:
        subnet = neutronclient.show_subnet(name_or_id)
        if subnet['subnet']['network_id'] != network_id:
            raise Exception('Subnet network mismatch while '
                            'using existing port.')

    if router_id:
        context.logger.info(
            'Attaching subnet "{0}" to router "{1}".'
            .format(subnet['subnet']['id'], router_id))
        neutronclient.add_interface_router(
            router_id, {'subnet_id': subnet['subnet']['id']})

    return subnet['subnet']


async def delete(context, name_or_id, neutronclient,
                 router_id=None, use_existing=False,
                 task_retry_interval=None,
                 task_retries=None):
    """
    Deletes subnet for given network
    :param context:
    :param name_or_id:
    :param neutronclient:
    :param router_id:
    :param use_existing:
    :param task_retry_interval:
    :param task_retries:
    :return:
    """
    if router_id:
        context.logger.info('Detaching subnet "{0}" '
                            'to router "{1}".'
                            .format(name_or_id, router_id))
        neutronclient.remove_interface_router(
            router_id, {'subnet_id': name_or_id})

    if not use_existing:

        neutronclient.delete_subnet(name_or_id)

        async def is_gone():
            try:
                neutronclient.show_subnet(name_or_id)
                return False
            except Exception as ex:
                context.logger.debug(str(ex))
                return True

        await utils.retry(is_gone, exceptions=(Exception,),
                          task_retries=task_retries,
                          task_retry_interval=task_retry_interval)
    else:
        context.logger.info('Subnet "{0}" remains as is, '
                            'because it is external resource.'
                            .format(name_or_id))
