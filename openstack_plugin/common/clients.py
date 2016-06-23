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

from glanceclient.v2 import client as glanceclient

from keystoneauth1 import loading
from keystoneauth1 import session
from keystoneclient import client as keystoneclient

from novaclient import client as novaclient
from neutronclient.v2_0 import client as neutronclient


class OpenStackClients(object):
    __keystone = None
    __nova = None
    __neutron = None
    __glance = None

    def __password_session_setup(self, node):
        creds = node.runtime_properties['auth_properties']
        if 'region_name' in creds:
            del creds['region_name']
        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(**creds)
        sess = session.Session(auth=auth)
        return sess

    def keystone(self, node):
        if self.__keystone is None:
            self.__keystone = keystoneclient.Client(**node.properties)
            self.__keystone.authenticate()
        return self.__keystone

    def nova(self, node):
        if self.__nova is None:
            version = node.properties['compute_api_version']
            use_connection_pool = node.properties['use_connection_pool']
            self.__nova = novaclient.Client(
                version, session=self.__password_session_setup(node),
                connection_pool=use_connection_pool)
        return self.__nova

    def neutron(self, node):
        if self.__neutron is None:
            self.__neutron = neutronclient.Client(
                session=self.__password_session_setup(node))
        return self.__neutron

    def glance(self, node):
        if self.__glance is None:
            self.__glance = glanceclient.Client(
                session=self.__password_session_setup(node))
        return self.__glance


openstack = OpenStackClients()
