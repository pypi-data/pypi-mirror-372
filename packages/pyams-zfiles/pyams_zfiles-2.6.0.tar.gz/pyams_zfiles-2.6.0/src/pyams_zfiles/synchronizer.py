#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_zfiles.synchronizer module

This module defines a synchronizer class, which is used to copy documents from
local container to a remote one.
"""

from xmlrpc.client import Binary, Fault

from ZODB.POSException import POSError
from persistent import Persistent
from pyramid.httpexceptions import HTTPNotFound
from zope.container.contained import Contained
from zope.container.folder import Folder
from zope.interface import implementer
from zope.schema import getFieldNames
from zope.schema.fieldproperty import FieldProperty
from zope.traversing.interfaces import ITraversable

from pyams_security.interfaces import IDefaultProtectionPolicy, IRolesPolicy, IViewContextPermissionChecker
from pyams_security.interfaces.names import UNCHANGED_PASSWORD
from pyams_security.property import RolePrincipalsFieldProperty
from pyams_security.security import ProtectedObjectMixin, ProtectedObjectRoles
from pyams_utils.adapter import ContextAdapter, adapter_config, get_annotation_adapter
from pyams_utils.factory import factory_config
from pyams_utils.protocol.xmlrpc import get_client
from pyams_utils.traversing import get_parent
from pyams_zfiles.interfaces import DELETE_MODE, DOCUMENT_SYNCHRONIZER_KEY, EXPORT_MODE, IDocumentContainer, \
    IDocumentRoles, IDocumentSynchronizer, IDocumentSynchronizerConfiguration, IDocumentSynchronizerConfigurationRoles, \
    IDocumentVersion, IMPORT_MODE, \
    MANAGE_APPLICATION_PERMISSION, SynchronizerStatus

__docformat__ = 'restructuredtext'


IMPORT_FIELDS = ('title', 'application_name', 'filename', 'properties',
                 'tags', 'status', 'owner', 'creator', 'created_time',
                 'access_mode', 'readers', 'update_mode', 'managers')


@factory_config(IDocumentSynchronizerConfiguration)
@implementer(IDefaultProtectionPolicy)
class DocumentSynchronizerConfiguration(ProtectedObjectMixin, Persistent, Contained):
    """Document synchronizer configuration"""

    name = FieldProperty(IDocumentSynchronizerConfiguration['name'])
    target = FieldProperty(IDocumentSynchronizerConfiguration['target'])
    username = FieldProperty(IDocumentSynchronizerConfiguration['username'])
    _password = FieldProperty(IDocumentSynchronizerConfiguration['password'])
    mode = FieldProperty(IDocumentSynchronizerConfiguration['mode'])
    enabled = FieldProperty(IDocumentSynchronizerConfiguration['enabled'])

    @property
    def password(self):
        """Password getter"""
        return self._password

    @password.setter
    def password(self, value):
        """Password setter"""
        if value == UNCHANGED_PASSWORD:
            return
        self._password = value

    def get_client(self):
        """XML-RPC client getter"""
        if not (self.target and self.enabled):
            return None
        return get_client(self.target, (self.username, self.password), allow_none=True)


@implementer(IDocumentSynchronizerConfigurationRoles)
class DocumentSynchronizerConfigurationRoles(ProtectedObjectRoles):
    """Document synchronizer configuration roles"""

    users = RolePrincipalsFieldProperty(IDocumentSynchronizerConfigurationRoles['users'])


@adapter_config(required=IDocumentSynchronizerConfiguration,
                provides=IDocumentSynchronizerConfigurationRoles)
def document_synchronizer_configuration_roles_adapter(context):
    """Document synchronizer configuration roles adapter"""
    return DocumentSynchronizerConfigurationRoles(context)


@adapter_config(name='zfiles_synchronizer_roles',
                required=IDocumentSynchronizerConfiguration,
                provides=IRolesPolicy)
class DocumentSynchronizerConfigurationRolesPolicy(ContextAdapter):
    """Document synchronizer configuration roles policy"""

    roles_interface = IDocumentSynchronizerConfigurationRoles
    weight = 20


@adapter_config(required=IDocumentSynchronizerConfiguration,
                provides=IViewContextPermissionChecker)
class DocumentSynchronizerConfigurationPermissionChecker(ContextAdapter):
    """Document synchronizer configuration permission checker"""

    edit_permission = MANAGE_APPLICATION_PERMISSION


@factory_config(IDocumentSynchronizer)
class DocumentSynchronizer(Folder):
    """Document synchronizer class"""

    __name__ = '++synchronizer++'

    def push(self, oid, mode=IMPORT_MODE, request=None, configuration=None):  # pylint: disable=unused-argument
        """Push document with given OID to remote container"""
        if configuration is None:
            return mode, SynchronizerStatus.ERROR.value
        try:
            client = configuration.get_client()
            if mode == IMPORT_MODE:
                document = IDocumentContainer(self.__parent__).get_document(oid)
                if document is None:
                    return mode, SynchronizerStatus.NOT_FOUND.value
                data = Binary(document.data.data)
                properties = document.to_json(IMPORT_FIELDS)
                client.importFile(oid, data, properties)
            elif mode == DELETE_MODE:
                client.deleteFile(oid)
            return mode, SynchronizerStatus.OK.value
        except POSError:
            return mode, SynchronizerStatus.NO_DATA.value
        except Fault:
            return mode, SynchronizerStatus.ERROR.value

    def pull(self, oid, mode=IMPORT_MODE, request=None, configuration=None):
        """Get document with given OID from remote container"""
        if configuration is None:
            return mode, SynchronizerStatus.ERROR.value
        container = IDocumentContainer(self.__parent__)
        try:
            if mode == IMPORT_MODE:
                client = configuration.get_client()
                properties = client.getFileProperties(oid, None, None, None, True)
                data = properties.pop('data', None)
                if isinstance(data, Binary):
                    data = data.data
                if not data:
                    return mode, SynchronizerStatus.NO_DATA.value
                schema = getFieldNames(IDocumentVersion) + getFieldNames(IDocumentRoles) + [
                    'filename', 'created_time', 'status'
                ]
                for name in list(properties.keys()):
                    if name not in schema:
                        properties.pop(name)
                document = container.get_document(oid)
                if document is None:
                    container.import_document(oid, data, properties)
                else:
                    properties.pop('created_time', None)
                    container.update_document(oid, None, data, properties)
            elif mode == DELETE_MODE:
                container.delete_document(oid)
            return mode, SynchronizerStatus.OK.value
        except POSError:
            return mode, SynchronizerStatus.NO_DATA.value
        except Fault:
            return mode, SynchronizerStatus.ERROR.value

    def synchronize_all(self, imported=None, deleted=None, request=None,
                        configuration=None):
        """Synchronize given OIDs, in import or delete modes, with a remote container"""
        if configuration is None:
            raise HTTPNotFound()
        action = self.push if configuration.mode == EXPORT_MODE else self.pull
        result = {}
        for oid in (imported or ()):
            result[oid] = action(oid, IMPORT_MODE, request, configuration)
        for oid in (deleted or ()):
            result[oid] = action(oid, DELETE_MODE, request, configuration)
        return result


@adapter_config(required=IDocumentContainer,
                provides=IDocumentSynchronizer)
def document_container_synchronizer(context):
    """Document container synchronizer adapter"""
    return get_annotation_adapter(context, DOCUMENT_SYNCHRONIZER_KEY, IDocumentSynchronizer,
                                  name='++synchronizer++')


@adapter_config(name='synchronizer',
                required=IDocumentContainer,
                provides=ITraversable)
class DocumentContainerSynchronizerTraverser(ContextAdapter):
    """Document container synchronizer traverser"""

    def traverse(self, name, furtherPath=None):  # pylint: disable=invalid-name, unused-argument
        """Document container traverser to synchronizer"""
        return IDocumentSynchronizer(self.context)
