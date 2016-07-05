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

import getpass
import os

path = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)), '../../../examples')

CONFIG = {
    # auth related
    'keystone_username': os.environ.get('OS_USERNAME', ''),
    'keystone_password': os.environ.get('OS_PASSWORD', ''),
    'keystone_project_name': os.environ.get('OS_PROJECT_NAME', ''),
    'keystone_url': os.environ.get('OS_AUTH_URL', ''),
    'openstack_region': os.environ.get('OS_AUTH_REGION', ''),
    'ssh_keypair_name': 'existing',
    'compute_name': 'test-vm',
    'compute_flavor': '196235bc-7ca5-4085-ac81-7e0242bda3f9',
    'compute_image': '6c3047c6-17b1-4aaf-a657-9229bb481e50',
    'network_name': 'tosca-net',
    'subnet_name': 'tosca-net-subnet',
    'subnet_ip_version': 4,
    'subnet_cidr': '10.0.3.0/24',
    'subnet_pool_start_ip': '10.0.3.2',
    'subnet_pool_end_ip': '10.0.3.254',
    'subnet_gateway_ip': '10.0.3.1',
    'subnet_dns_nameserver': ['8.8.8.8', '8.8.4.4'],
    'network_port_name': 'tosca-net-port',
    'network_subnet_port_name': 'tosca-net-subnet-port',
    'new_network_subnet_port_name': 'tosca-net-subnet-port-new',
    'router_name': 'tosca-net-router',
    'external_network_id': '6751cb30-0aef-4d7e-94c3-ee2a09e705eb',

    'inbound_subnet_name': 'tosca-net-inbound-subnet',
    'inbound_subnet_cidr': '10.0.3.0/24',
    'inbound_subnet_pool_start_ip': '10.0.3.2',
    'inbound_subnet_pool_end_ip': '10.0.3.254',
    'inbound_subnet_gateway_ip': '10.0.3.1',
    'inbound_network_name': 'inbound-net',
    'inbound_network_subnet_port': 'inbound-port',

    'mgmt_subnet_name': 'tosca-net-mgm-subnet',
    'mgmt_subnet_cidr': '10.0.5.0/24',
    'mgmt_subnet_pool_start_ip': '10.0.5.2',
    'mgmt_subnet_pool_end_ip': '10.0.5.254',
    'mgmt_subnet_gateway_ip': '10.0.5.1',
    'mgmt_network_subnet_port': 'mgmt-port',
    'mgmt_network_name': 'mgmt-net',

    'outbound_subnet_name': 'tosca-net-outbound-subnet',
    'outbound_subnet_cidr': '10.0.4.0/24',
    'outbound_subnet_pool_start_ip': '10.0.4.2',
    'outbound_subnet_pool_end_ip': '10.0.4.254',
    'outbound_subnet_gateway_ip': '10.0.4.1',
    'outbound_network_subnet_port': 'outbound-port',
    'outbound_network_name': 'outbound-net',

    'compute_name_one': 'test-vm-1',
    'compute_name_two': 'test-vm-2',

    'inbound_network_subnet_port_one': 'one.new',
    'outbound_network_subnet_port_one': 'two.new',

    'install_script': os.path.join(path, 'scripts', 'check_injection.sh'),
    'local_file_path_for_injection': os.path.join(path, 'injection', 'file'),
    'remote_file_path_for_injection': '/tmp/file',
    'username': os.environ.get('USERNAME', getpass.getuser()),
    'ssh_port': os.environ.get('SSH_PORT', 22),
    'userdata_script_path': os.path.join(path, 'userdata',
                                         'docker-ubuntu-16-04.sh'),
    'lb_algorithm': 'LEAST_CONNECTIONS',
    'lb_protocol': 'TCP',
}
