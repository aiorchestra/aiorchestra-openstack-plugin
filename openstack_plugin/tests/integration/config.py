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

import os


CONFIG = {
    # auth related
    'keystone_username': os.environ.get('OS_USERNAME', ''),
    'keystone_password': os.environ.get('OS_PASSWORD', ''),
    'keystone_project_name': os.environ.get('OS_PROJECT_NAME', ''),
    'keystone_url': os.environ.get('OS_AUTH_URL', ''),
    'openstack_region': os.environ.get('OS_AUTH_REGION', ''),
    # compute related
    'compute_name': 'compute-instance',
    'compute_flavor': '196235bc-7ca5-4085-ac81-7e0242bda3f9',
    'compute_image': '6c3047c6-17b1-4aaf-a657-9229bb481e50',
    'compute_name_one': 'test-vm-1',
    'compute_name_two': 'test-vm-2',
    'inbound_net_compute_name': 'inbound',
    'outbound_net_compute_name': 'outbound',
    # ssh keypair related
    'ssh_keypair_name': 'test-vm-ssh',
    'compute_keypair_name': 'test-vm-ssh',
    # networking related
    'network_name': 'test',
    'subnet_name': 'test-subnet',
    'subnet_ip_version': 4,
    'subnet_cidr': '10.0.3.0/24',
    'subnet_pools': [{
        'start': '10.0.3.20',
        'end': '10.0.3.150'
    }, ],
    'subnet_dns_nameservers': ['4.4.4.4', '8.8.8.8'],
    'subnet_port': 'test-subnet-port',
    'router_name': 'test-router',
    'network_name_one': 'test-one',
    'network_name_two': 'test-two',
    'network_name_three': 'mgmt',
    'subnet_name_one': 'test-subnet-one',
    'subnet_name_two': 'test-subnet-two',
    'subnet_name_three': 'mgmt-subnet',
    'subnet_cidr_one': '10.0.3.0/24',
    'subnet_cidr_two': '10.0.4.0/24',
    'subnet_cidr_three': '10.0.5.0/24',
    'subnet_pools_one': [{
        'start': '10.0.3.20',
        'end': '10.0.3.150'
    }, ],
    'subnet_pools_two': [{
        'start': '10.0.4.20',
        'end': '10.0.4.150'
    }, ],
    'subnet_pools_three': [{
        'start': '10.0.5.20',
        'end': '10.0.5.150'
    }, ],
    'ext_net_name': '6751cb30-0aef-4d7e-94c3-ee2a09e705eb',
    'subnet_port_one': 'port-one',
    'subnet_port_two': 'port-two',
    'subnet_port_three': 'port-mgmt',
    'inbound_port_name': 'compute-inbound-port',
    'outbound_port_name': 'compute-outbound-port',
    'security_group_name_or_id': 'demo',
    'security_group_description': 'demo',
}
