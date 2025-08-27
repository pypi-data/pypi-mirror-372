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

"""PyAMS_zfiles.document module

This module defines ZFiles documents.
"""

import io
from cgi import FieldStorage
from datetime import datetime, timezone
from hashlib import sha512

from hypatia.interfaces import ICatalog
from persistent import Persistent
from pyramid.interfaces import IRequest
from zope.container.contained import Contained
from zope.dublincore.interfaces import IZopeDublinCore
from zope.interface import Interface, implementer
from zope.intid import IIntIds
from zope.schema import getFieldNames
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from pyams_file.property import FileProperty
from pyams_security.interfaces import IDefaultProtectionPolicy, IRoleProtectedObject, \
    IRolesPolicy, IViewContextPermissionChecker
from pyams_security.interfaces.base import FORBIDDEN_PERMISSION
from pyams_security.property import RolePrincipalsFieldProperty
from pyams_security.security import ProtectedObjectMixin, ProtectedObjectRoles
from pyams_utils.adapter import ContextAdapter, ContextRequestViewAdapter, adapter_config
from pyams_utils.factory import factory_config
from pyams_utils.interfaces.form import NOT_CHANGED
from pyams_utils.registry import get_utility
from pyams_utils.request import check_request
from pyams_utils.timezone import tztime
from pyams_utils.traversing import get_parent
from pyams_utils.url import absolute_url
from pyams_utils.vocabulary import vocabulary_config
from pyams_workflow.interfaces import IWorkflowInfo, IWorkflowState
from pyams_zfiles.interfaces import ACCESS_MODE, DocumentContainerError, ICatalogPropertiesIndexesContainer, IDocument, \
    IDocumentContainer, IDocumentPropertyExtractorContainer, IDocumentRoles, IDocumentVersion, \
    MANAGE_APPLICATION_PERMISSION, \
    MANAGE_DOCUMENT_PERMISSION, PYAMS_ZFILES_APPLICATIONS_VOCABULARY, READ_DOCUMENT_PERMISSION, \
    ZFILES_WORKFLOW_NAME
from pyams_zfiles.workflow import ZFILES_WORKFLOW


__docformat__ = 'restructuredtext'


_marker = object()


def is_file_like(data):
    """Check for file-like object"""
    return hasattr(data, 'read') and hasattr(data, 'seek')


def get_hash(data):
    """Get hash for given data"""
    document_hash = sha512()
    if isinstance(data, FieldStorage):
        data = data.file
    if is_file_like(data):
        data.seek(0)
        value = data.read(io.DEFAULT_BUFFER_SIZE)
        while value:
            document_hash.update(value)
            value = data.read(io.DEFAULT_BUFFER_SIZE)
        data.seek(0)
    else:
        document_hash.update(data)
    return document_hash.hexdigest()


@factory_config(IDocumentVersion)
@implementer(IDefaultProtectionPolicy)
class DocumentVersion(ProtectedObjectMixin, Persistent, Contained):
    # pylint: disable=too-many-instance-attributes
    """Document version"""

    title = FieldProperty(IDocumentVersion['title'])
    application_name = FieldProperty(IDocumentVersion['application_name'])
    _data = FileProperty(IDocumentVersion['data'])
    hash = FieldProperty(IDocumentVersion['hash'])
    access_mode = FieldProperty(IDocumentVersion['access_mode'])
    update_mode = FieldProperty(IDocumentVersion['update_mode'])
    properties = FieldProperty(IDocumentVersion['properties'])
    _tags = FieldProperty(IDocumentVersion['tags'])
    updater = FieldProperty(IDocumentVersion['updater'])

    @property
    def oid(self):
        """Get parent OID"""
        document = get_parent(self, IDocument)
        return document.oid

    @property
    def data(self):
        """Document data getter"""
        return self._data

    @data.setter
    def data(self, value):
        """Document data setter"""
        if value is NOT_CHANGED:
            return
        if value is None:
            self._data = None
            return
        data = value
        filename = None
        if isinstance(data, tuple):
            filename, data = data
        if isinstance(data, FieldStorage):
            filename = data.filename
            data = data.file
        document_hash = get_hash(data)
        if document_hash == self.hash:
            return
        self._data = data
        self._data.filename = filename
        self.hash = document_hash

    @data.deleter
    def data(self):
        """Document data deleter"""
        del self._data

    @property
    def index_properties(self):
        """Document properties getter used for indexing"""
        if not self.properties:
            return None
        container = get_utility(IDocumentContainer)
        catalog_indexes = ICatalogPropertiesIndexesContainer(container)
        return [
            f'{key}={val}'
            for key, value in self.properties.items()
            for val in value.split(';')
            if val and (key not in catalog_indexes.index_names)
        ]
    
    def get_index_property(self, property_name, default=None):
        """Get specific index property value"""
        if not self.properties:
            return default
        value = self.properties.get(property_name, _marker)
        if value is _marker:
            return default
        return value.split(';') if value else None

    @property
    def tags(self):
        """Document tags getter"""
        return self._tags

    @tags.setter
    def tags(self, value):
        """Document tags setter"""
        if isinstance(value, str):
            value = map(str.strip, value.split(';'))
        value = list(value) if value else None
        self._tags = value

    def update(self, data, properties, request=None):
        """Document data setter"""
        if properties:
            if request is None:
                request = check_request()
            self.updater = request.principal.id
        if data is not None:
            if 'filename' in properties:
                data = (properties.pop('filename'), data)
            self.data = data
        if (not self.title) or ('title' in properties):
            self.title = properties.pop('title', '<UNDEFINED>')
        if (not self.application_name) or ('application_name' in properties):
            self.application_name = properties.pop('application_name', '<UNDEFINED>')
        self.update_roles(properties, request)
        self.update_security_policy(properties, request)
        self.update_status(properties, request)
        self.update_properties(properties, request)
        self.extract_properties(properties, request)
        self.update_title(properties, request)
        return IWorkflowState(self)

    def update_roles(self, properties, request=None):  # pylint: disable=unused-argument
        """Document roles setter"""
        roles = IDocumentRoles(self)
        if not roles.creator:
            creator = properties.pop('creator', None)
            if creator:
                roles.creator = creator
        if (not roles.owner) or ('owner' in properties):
            owner = properties.pop('owner', None)
            if owner:
                roles.owner = owner
        if (not roles.readers) or ('readers' in properties):
            readers = properties.pop('readers', None)
            if readers:
                if isinstance(readers, str):
                    readers = map(str.strip, readers.split(';'))
                roles.readers = set(readers) if readers else None
        if (not roles.managers) or ('managers' in properties):
            managers = properties.pop('managers', None)
            if managers:
                if isinstance(managers, str):
                    managers = map(str.strip, managers.split(';'))
                roles.managers = set(managers) if managers else None

    def update_security_policy(self, properties, request=None):  # pylint: disable=unused-argument
        """Document policy security updater"""
        roles = IDocumentRoles(self)
        protection = IRoleProtectedObject(self)
        granted = protection.authenticated_granted or set()
        if (not self.access_mode) or ('access_mode' in properties):
            mode = properties.pop('access_mode', ACCESS_MODE.PRIVATE.value)
            try:
                access_mode = ACCESS_MODE(mode).value
            except ValueError:
                pass
            else:
                self.access_mode = access_mode
                if access_mode == ACCESS_MODE.PUBLIC.value:
                    granted |= {READ_DOCUMENT_PERMISSION}
                else:
                    granted -= {READ_DOCUMENT_PERMISSION}
                    if access_mode == ACCESS_MODE.PRIVATE.value:
                        roles.readers = set()
        if (not self.update_mode) or ('update_mode' in properties):
            mode = properties.pop('update_mode', ACCESS_MODE.PRIVATE.value)
            try:
                update_mode = ACCESS_MODE(mode).value
            except ValueError:
                pass
            else:
                self.update_mode = update_mode
                if update_mode == ACCESS_MODE.PUBLIC.value:
                    granted |= {MANAGE_DOCUMENT_PERMISSION}
                else:
                    granted -= {MANAGE_DOCUMENT_PERMISSION}
                    if update_mode == ACCESS_MODE.PRIVATE.value:
                        roles.managers = set()
        protection.authenticated_granted = granted or None

    def update_status(self, properties, request=None):
        """Workflow status updater"""
        if 'status' in properties:
            info = IWorkflowInfo(self)
            info.fire_transition_toward(properties.pop('status'), request=request)

    def update_properties(self, properties, request=None):  # pylint: disable=unused-argument
        """Document properties updater"""
        if 'tags' in properties:
            self.tags = properties.pop('tags', None)
        # properties cleanup
        schema = getFieldNames(IDocumentVersion) + getFieldNames(IDocumentRoles)
        schema.remove('properties')
        for key in list(properties.keys()):
            if key in schema:
                properties.pop(key)
        if properties:
            # mix 'properties' value with custom properties
            props = properties.pop('properties', {})
            props.update(properties)
            if props:
                self_props = self.properties or {}
                self_props.update(props)
                for key, val in list(self_props.items()):
                    if val is None:
                        del self_props[key]
                self.properties = self_props or None
                
    def extract_properties(self, properties, request=None):
        """Use extractors to get properties fron document content"""
        manager = get_utility(IDocumentContainer)
        extractors = IDocumentPropertyExtractorContainer(manager, None)
        if extractors is not None:
            props = extractors.extract_properties(self)
            if props:
                self_props = self.properties or {}
                self_props.update(props)
                self.properties = self_props or {}
                
    def update_title(self, properties, request=None):
        """Update document title from properties"""
        properties = (self.properties or {}).copy()
        properties['now'] = tztime(datetime.now(timezone.utc))
        try:
            self.title = self.title.format(**properties)
        except KeyError:
            pass
        try:
            self.data.filename = self.data.filename.format(**properties)
        except KeyError:
            pass

    def to_json(self, fields=None, request=None):
        """Get document properties in JSON format"""
        if request is None:
            request = check_request()
        dc = IZopeDublinCore(self)  # pylint: disable=invalid-name
        state = IWorkflowState(self)
        roles = IDocumentRoles(self)
        result = {
            'api': absolute_url(request.root, request, 'api/zfiles/rest/{}'.format(self.oid)),
            'oid': self.oid,
            'title': self.title,
            'application_name': self.application_name,
            'filename': self.data.filename,
            'filesize': self.data.get_size(),
            'content_type': self.data.content_type,
            'href': absolute_url(self.data, request),
            'hash': self.hash,
            'properties': self.properties or {},
            'tags': list(self.tags or ()),
            'version': state.version_id,
            'status': state.state,
            'creator': list(roles.creator)[0],
            'created_time': dc.created.isoformat() if dc.created else None,  # pylint: disable=no-member
            'owner': list(roles.owner)[0],
            'updater': self.updater,
            'updated_time': dc.modified.isoformat() if dc.modified else None,  # pylint: disable=no-member
            'status_updater': state.state_principal,
            'status_update_time': state.state_date.isoformat(),  # pylint: disable=no-member
            'access_mode': self.access_mode,
            'readers': list(roles.readers or ()),
            'update_mode': self.update_mode,
            'managers': list(roles.managers or ())
        }
        if fields:
            for key in tuple(result.keys()):
                if key not in fields:
                    del result[key]
        return result


@implementer(IDocumentRoles)
class DocumentRoles(ProtectedObjectRoles):
    """Document roles"""

    creator = RolePrincipalsFieldProperty(IDocumentRoles['creator'])
    owner = RolePrincipalsFieldProperty(IDocumentRoles['owner'])
    readers = RolePrincipalsFieldProperty(IDocumentRoles['readers'])
    managers = RolePrincipalsFieldProperty(IDocumentRoles['managers'])


@adapter_config(required=IDocumentVersion,
                provides=IDocumentRoles)
def document_roles_adapter(context):
    """Document roles"""
    return DocumentRoles(context)


@adapter_config(required=IDocumentVersion,
                provides=IRolesPolicy)
class DocumentRolesPolicy(ContextAdapter):
    """Document roles policy"""

    roles_interface = IDocumentRoles
    weight = 10


@adapter_config(required=(IDocumentVersion, IRequest, Interface),
                provides=IViewContextPermissionChecker)
class DocumentPermissionChecker(ContextRequestViewAdapter):
    """Document permission checker"""

    @property
    def edit_permission(self):
        """Document edit permission getter"""
        document = self.context
        request = self.request
        if request.has_permission(MANAGE_APPLICATION_PERMISSION, context=self):
            return MANAGE_APPLICATION_PERMISSION
        state = IWorkflowState(document)
        if state in ZFILES_WORKFLOW.visible_states:
            return FORBIDDEN_PERMISSION
        return MANAGE_DOCUMENT_PERMISSION


@factory_config(IDocument)
class Document(Persistent, Contained):
    """Main document class"""

    content_class = IDocument

    workflow_name = FieldProperty(IDocument['workflow_name'])
    view_permission = FieldProperty(IDocument['view_permission'])

    oid = FieldProperty(IDocument['oid'])

    def __init__(self):
        self.workflow_name = ZFILES_WORKFLOW_NAME

    def get_oid(self):
        """Get new document OID"""
        container = get_utility(IDocumentContainer)
        intids = get_utility(IIntIds)
        oid = '{}{}'.format(container.oid_prefix or '',
                            hex(intids.register(self))[2:])
        if container.get_document(oid) is not None:
            raise DocumentContainerError("Specified OID already exists!")
        self.oid = oid


@vocabulary_config(PYAMS_ZFILES_APPLICATIONS_VOCABULARY)
class ApplicationsVocabulary(SimpleVocabulary):
    """Registered applications vocabulary"""

    def __init__(self, context=None):  # pylint: disable=unused-argument
        catalog = get_utility(ICatalog)
        index = catalog['zfile_application']
        terms = [
            SimpleTerm(v, title=v) for v in index.unique_values()
        ]
        super().__init__(terms)
