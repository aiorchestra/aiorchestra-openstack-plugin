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


async def create(context, name_or_id, neutronclient,
                 description=None, use_existing=False):
    """
    Creates security group
    :param context:
    :param name_or_id:
    :param neutronclient:
    :param description:
    :param use_existing:
    :return:
    """
    if not use_existing:
        sg_dict = {
            'security_group': {
                'description': description,
                'name': name_or_id,
            }
        }
        sg = neutronclient.create_security_group(
            body=sg_dict)
    else:
        sg = neutronclient.show_security_group(name_or_id)

    return sg['security_group']


async def create_rules(context, security_group_id,
                       rules, neutronclient):
    """
    Creates security group rules
    :param context:
    :param security_group_id:
    :param rules:
    :param neutronclient:
    :return:
    """
    for rule in rules:
        rule.update(security_group_id=security_group_id)
        context.logger.info(
            'Attempting to create rule for '
            'security group "{0}".'
            .format(security_group_id))
        _r = neutronclient.create_security_group_rule(
            {'security_group_rule': rule}
        )['security_group_rule']
        context.logger.info('Security group rule create: "{0}".'
                            .format(_r['id']))


async def delete(context, name_or_id,
                 neutronclient, use_existing=False):
    if use_existing:
        context.logger.info('Leaving security groups as is '
                            'because it is an external resource.')
        return
    neutronclient.delete_security_group(name_or_id)
    context.logger.info('Security group "{0}" deleted.'
                        .format(name_or_id))
