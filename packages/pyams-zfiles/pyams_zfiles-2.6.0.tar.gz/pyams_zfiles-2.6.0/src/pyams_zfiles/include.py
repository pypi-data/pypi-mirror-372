#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_zfiles.include module

This module is used for Pyramid integration.
"""

import re

from pyramid_rpc.xmlrpc import XMLRPCRenderer

from pyams_security.interfaces.base import MANAGE_ROLES_PERMISSION, ROLE_ID
from pyams_security.interfaces.names import ADMIN_USER_ID, SYSTEM_ADMIN_ROLE
from pyams_zfiles.interfaces import CREATE_DOCUMENT_PERMISSION, CREATE_DOCUMENT_WITH_OWNER_PERMISSION, GRAPHQL_API_PATH, \
    GRAPHQL_API_ROUTE, JSONRPC_ENDPOINT, JSONRPC_PATH, MANAGE_APPLICATION_PERMISSION, MANAGE_DOCUMENT_PERMISSION, \
    READ_DOCUMENT_PERMISSION, REST_CONTAINER_PATH, REST_CONTAINER_ROUTE, REST_DOCUMENT_PATH, REST_DOCUMENT_ROUTE, \
    REST_SYNCHRONIZER_PATH, REST_SYNCHRONIZER_ROUTE, SYNCHRONIZE_PERMISSION, XMLRPC_ENDPOINT, XMLRPC_PATH, \
    ZFILES_ADMIN_ROLE, ZFILES_CREATOR_ROLE, ZFILES_IMPORTER_ROLE, ZFILES_MANAGER_ROLE, ZFILES_OWNER_ROLE, \
    ZFILES_READER_ROLE, ZFILES_SYNCHRONIZER_ROLE

__docformat__ = 'restructuredtext'

from pyams_zfiles import _


def include_package(config):
    """Pyramid package include"""

    # add translations
    config.add_translation_dirs('pyams_zfiles:locales')

    # register new ZFiles permissions
    config.register_permission({
        'id': MANAGE_APPLICATION_PERMISSION,
        'title': _("Manage ZFiles application")
    })
    config.register_permission({
        'id': SYNCHRONIZE_PERMISSION,
        'title': _("Synchronize documents")
    })
    config.register_permission({
        'id': CREATE_DOCUMENT_PERMISSION,
        'title': _("Create new document")
    })
    config.register_permission({
        'id': CREATE_DOCUMENT_WITH_OWNER_PERMISSION,
        'title': _("Create new document (with specified owner)")
    })
    config.register_permission({
        'id': MANAGE_DOCUMENT_PERMISSION,
        'title': _("Manage document")
    })
    config.register_permission({
        'id': READ_DOCUMENT_PERMISSION,
        'title': _("Read document")
    })

    # upgrade system manager role
    config.upgrade_role(SYSTEM_ADMIN_ROLE,
                        permissions={
                            MANAGE_APPLICATION_PERMISSION,
                            CREATE_DOCUMENT_PERMISSION,
                            CREATE_DOCUMENT_WITH_OWNER_PERMISSION,
                            MANAGE_DOCUMENT_PERMISSION,
                            READ_DOCUMENT_PERMISSION
                        })

    # register new roles
    config.register_role({
        'id': ZFILES_ADMIN_ROLE,
        'title': _("ZFiles application manager (role)"),
        'permissions': {
            MANAGE_APPLICATION_PERMISSION,
            MANAGE_ROLES_PERMISSION,
            CREATE_DOCUMENT_WITH_OWNER_PERMISSION
        },
        'managers': {
            ADMIN_USER_ID,
            ROLE_ID.format(SYSTEM_ADMIN_ROLE)
        }
    })
    config.register_role({
        'id': ZFILES_SYNCHRONIZER_ROLE,
        'title': _("Documents synchronizer (role)"),
        'permissions': {
            SYNCHRONIZE_PERMISSION
        },
        'managers': {
            ADMIN_USER_ID,
            ROLE_ID.format(SYSTEM_ADMIN_ROLE),
            ROLE_ID.format(ZFILES_ADMIN_ROLE)
        }
    })
    config.register_role({
        'id': ZFILES_IMPORTER_ROLE,
        'title': _("Documents importer (role)"),
        'permissions': {
            CREATE_DOCUMENT_PERMISSION,
            CREATE_DOCUMENT_WITH_OWNER_PERMISSION,
            MANAGE_DOCUMENT_PERMISSION,
            READ_DOCUMENT_PERMISSION
        },
        'managers': {
            ADMIN_USER_ID,
            ROLE_ID.format(SYSTEM_ADMIN_ROLE),
            ROLE_ID.format(ZFILES_ADMIN_ROLE)
        }
    })
    config.register_role({
        'id': ZFILES_MANAGER_ROLE,
        'title': _("Document manager (role)"),
        'permissions': {
            CREATE_DOCUMENT_PERMISSION,
            MANAGE_DOCUMENT_PERMISSION,
            READ_DOCUMENT_PERMISSION
        },
        'managers': {
            ADMIN_USER_ID,
            ROLE_ID.format(SYSTEM_ADMIN_ROLE),
            ROLE_ID.format(ZFILES_ADMIN_ROLE)
        }
    })
    config.register_role({
        'id': ZFILES_CREATOR_ROLE,
        'title': _("Document creator (role)"),
        'managers': {
            ADMIN_USER_ID,
            ROLE_ID.format(SYSTEM_ADMIN_ROLE),
            ROLE_ID.format(ZFILES_ADMIN_ROLE)
        }
    })
    config.register_role({
        'id': ZFILES_OWNER_ROLE,
        'title': _("Document owner (role)"),
        'permissions': {
            MANAGE_DOCUMENT_PERMISSION,
            READ_DOCUMENT_PERMISSION
        },
        'managers': {
            ADMIN_USER_ID,
            ROLE_ID.format(SYSTEM_ADMIN_ROLE),
            ROLE_ID.format(ZFILES_ADMIN_ROLE)
        }
    })
    config.register_role({
        'id': ZFILES_READER_ROLE,
        'title': _("Document reader (role)"),
        'permissions': {
            READ_DOCUMENT_PERMISSION
        },
        'managers': {
            ADMIN_USER_ID,
            ROLE_ID.format(SYSTEM_ADMIN_ROLE),
            ROLE_ID.format(ZFILES_ADMIN_ROLE),
            ROLE_ID.format(ZFILES_OWNER_ROLE),
            ROLE_ID.format(ZFILES_MANAGER_ROLE)
        }
    })

    # register new REST API routes
    config.add_route(REST_CONTAINER_ROUTE,
                     config.registry.settings.get(f'{REST_CONTAINER_ROUTE}_route.path',
                                                  REST_CONTAINER_PATH))
    config.add_route(REST_SYNCHRONIZER_ROUTE,
                     config.registry.settings.get(f'{REST_SYNCHRONIZER_ROUTE}_route.path',
                                                  REST_SYNCHRONIZER_PATH))
    config.add_route(REST_DOCUMENT_ROUTE,
                     config.registry.settings.get(f'{REST_DOCUMENT_ROUTE}_route.path',
                                                  REST_DOCUMENT_PATH))

    # register new GraphQL API route
    config.add_route(GRAPHQL_API_ROUTE,
                     config.registry.settings.get(f'{GRAPHQL_API_ROUTE}_route.path',
                                                  GRAPHQL_API_PATH))

    # register new RPC endpoints
    config.add_jsonrpc_endpoint(JSONRPC_ENDPOINT,
                                config.registry.settings.get(f'{JSONRPC_ENDPOINT}_route.path',
                                                             JSONRPC_PATH))

    config.add_renderer('xmlrpc-with-none', XMLRPCRenderer(allow_none=True))
    config.add_xmlrpc_endpoint(XMLRPC_ENDPOINT,
                               config.registry.settings.get(f'{XMLRPC_ENDPOINT}_route.path',
                                                            XMLRPC_PATH),
                               default_renderer='xmlrpc-with-none')

    # package scan
    ignored = []
    try:
        import pyams_zmi  # pylint: disable=import-outside-toplevel,unused-import
    except ImportError:
        ignored.append(re.compile(r'pyams_zfiles\..*\.zmi\.?.*').search)

    try:
        import pyams_scheduler  # pylint: disable=import-outside-toplevel,unused-import
        import pyams_alchemy  # pylint: disable=import-outside-toplevel,unused-import
    except ImportError:
        ignored.append('pyams_zfiles.task')

    config.scan(ignore=ignored)
