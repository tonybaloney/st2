# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Module for loading RBAC role definitions and grants from the filesystem.
"""

import os
import glob

from oslo_config import cfg

from st2common import log as logging
from st2common.content.loader import MetaLoader
from st2common.models.api.rbac import RoleDefinitionFileFormatAPI
from st2common.models.api.rbac import UserRoleAssignmentFileFormatAPI
from st2common.util.misc import compare_path_file_name

LOG = logging.getLogger(__name__)

__all__ = [
    'RBACDefinitionsLoader'
]


class RBACDefinitionsLoader(object):
    """
    A class which loads role definitions and user role assignments from files on
    disk.
    """

    def __init__(self):
        base_path = cfg.CONF.system.base_path
        rbac_definitions_path = os.path.join(base_path, 'rbac/')

        self._role_definitions_path = os.path.join(rbac_definitions_path, 'roles/')
        self._role_assignments_path = os.path.join(rbac_definitions_path, 'assignments/')
        self._meta_loader = MetaLoader()

    def load(self):
        """
        :return: Dict with the following keys: roles, role_assiginments
        :rtype: ``dict``
        """
        result = {}
        result['roles'] = self.load_role_definitions()
        result['role_assignments'] = self.load_user_role_assignments()

        return result

    def load_role_definitions(self):
        """
        Load all the role definitions.

        :rtype: ``dict``
        """
        LOG.info('Loading role definitions from "%s"' % (self._role_definitions_path))
        file_paths = self._get_role_definitions_file_paths()

        result = {}
        for file_path in file_paths:
            LOG.debug('Loading role definition from: %s' % (file_path))
            role_definition_api = self.load_role_definition_from_file(file_path=file_path)
            role_name = role_definition_api.name

            if role_name in result:
                raise ValueError('Duplicate definition file found for role "%s"' % (role_name))

            result[role_name] = role_definition_api

        return result

    def load_user_role_assignments(self):
        """
        Load all the user role assignments.

        :rtype: ``dict``
        """
        LOG.info('Loading user role assignments from "%s"' % (self._role_assignments_path))
        file_paths = self._get_role_assiginments_file_paths()

        result = {}
        for file_path in file_paths:
            LOG.debug('Loading user role assignments from: %s' % (file_path))
            role_assignment_api = self.load_user_role_assignments_from_file(file_path=file_path)
            username = role_assignment_api.username

            if username in result:
                raise ValueError('Duplicate definition file found for user "%s"' % (username))

            result[username] = role_assignment_api

        return result

    def load_role_definition_from_file(self, file_path):
        """
        Load role definition from file.

        :param file_path: Path to the role definition file.
        :type file_path: ``str``

        :return: Role definition.
        :rtype: :class:`RoleDefinitionFileFormatAPI`
        """
        content = self._meta_loader.load(file_path)

        role_definition_api = RoleDefinitionFileFormatAPI(**content)
        role_definition_api.validate()

        return role_definition_api

    def load_user_role_assignments_from_file(self, file_path):
        """
        Load user role assignments from file.

        :param file_path: Path to the user role assignment file.
        :type file_path: ``str``

        :return: User role assignments.
        :rtype: :class:`UserRoleAssignmentFileFormatAPI`
        """
        content = self._meta_loader.load(file_path)

        user_role_assignment_api = UserRoleAssignmentFileFormatAPI(**content)
        user_role_assignment_api.validate()

        return user_role_assignment_api

    def _get_role_definitions_file_paths(self):
        """
        Retrieve a list of paths for all the role definitions.

        Notes: Roles are sorted in an alphabetical order based on the role name.

        :rtype: ``list``
        """
        glob_str = self._role_definitions_path + '*.yaml'
        file_paths = glob.glob(glob_str)
        file_paths = sorted(file_paths, cmp=compare_path_file_name)
        return file_paths

    def _get_role_assiginments_file_paths(self):
        """
        Retrieve a list of paths for all the user role assignments.

        Notes: Assignments are sorted in an alphabetical order based on the username.

        :rtype: ``list``
        """
        glob_str = self._role_assignments_path + '*.yaml'
        file_paths = glob.glob(glob_str)
        file_paths = sorted(file_paths, cmp=compare_path_file_name)
        return file_paths