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

"""PyAMS_zfiles.utility module

This module provides main documents container utility classes.
"""

import datetime
from datetime import datetime, timezone
from xmlrpc.client import DateTime

from dateutil import parser
from hypatia.catalog import CatalogQuery
from hypatia.interfaces import ICatalog
from hypatia.query import Eq
from pyramid.httpexceptions import HTTPBadRequest, HTTPCreated, HTTPForbidden, HTTPNotFound
from zope.container.folder import Folder
from zope.interface import implementer
from zope.lifecycleevent import ObjectAddedEvent, ObjectCreatedEvent, ObjectModifiedEvent
from zope.location import locate
from zope.location.interfaces import ISublocations
from zope.schema.fieldproperty import FieldProperty

from pyams_catalog.query import CatalogResultSet, ResultSet, and_
from pyams_security.interfaces import IDefaultProtectionPolicy, IRolesPolicy
from pyams_security.property import RolePrincipalsFieldProperty
from pyams_security.security import ProtectedObjectMixin, ProtectedObjectRoles
from pyams_site.interfaces import ISiteRoot
from pyams_utils.adapter import ContextAdapter, adapter_config
from pyams_utils.factory import factory_config
from pyams_utils.list import unique_iter
from pyams_utils.registry import get_utility, query_utility
from pyams_utils.request import check_request
from pyams_utils.traversing import get_parent
from pyams_workflow.interfaces import IWorkflowInfo, IWorkflowState, IWorkflowVersions
from pyams_workflow.versions import get_last_version
from pyams_zfiles.document import Document, DocumentVersion, get_hash
from pyams_zfiles.folder import DocumentFolder
from pyams_zfiles.interfaces import CREATE_DOCUMENT_WITH_OWNER_PERMISSION, ICatalogPropertiesIndexesContainerTarget, \
    IDocumentContainer, IDocumentContainerRoles, IDocumentFolder, IDocumentPropertyExtractorContainerTarget, \
    IDocumentVersion, MANAGE_DOCUMENT_PERMISSION, READ_DOCUMENT_PERMISSION, STATE
from pyams_zfiles.search import make_query

__docformat__ = 'restructuredtext'

from pyams_zfiles import _


@factory_config(IDocumentContainer)
@implementer(IDefaultProtectionPolicy, ICatalogPropertiesIndexesContainerTarget,
             IDocumentPropertyExtractorContainerTarget)
class DocumentContainer(ProtectedObjectMixin, Folder):
    """Document container utility"""

    oid_prefix = FieldProperty(IDocumentContainer['oid_prefix'])
    show_home_menu = FieldProperty(IDocumentContainer['show_home_menu'])

    def _get_folder(self, creation_date):
        """Get document storage folder"""
        year = str(creation_date.year)
        year_folder = self.get(year)
        if year_folder is None:
            year_folder = self[year] = DocumentFolder()
        month = '{:02}'.format(creation_date.month)
        month_folder = year_folder.get(month)
        if month_folder is None:
            month_folder = year_folder[month] = DocumentFolder()
        return month_folder

    @staticmethod
    def _create_document(registry, folder):
        """Create new document and version"""
        document = Document()
        registry.notify(ObjectCreatedEvent(document))
        locate(document, folder)
        version = DocumentVersion()
        registry.notify(ObjectCreatedEvent(version))
        # add version to document
        versions = IWorkflowVersions(document)
        versions.add_version(version, None)
        IWorkflowInfo(version).fire_transition('init')
        return document, version

    def add_document(self, data, properties, request=None):
        """Add new document"""
        if request is None:
            request = check_request()
        registry = request.registry
        # check required properties
        properties = properties.copy()
        title = properties.get('title')
        application_name = properties.get('application_name')
        if (not title) or (not application_name) or (data is None):
            raise HTTPBadRequest("Missing arguments")
        owner = properties.get('owner')
        if owner and not request.has_permission(CREATE_DOCUMENT_WITH_OWNER_PERMISSION,
                                                context=self):
            raise HTTPForbidden()
        if not owner:
            properties['owner'] = request.principal.id
        properties['creator'] = request.principal.id
        # check storage folders
        created_time = properties.pop('created_time', None)
        if isinstance(created_time, DateTime):
            folder = self._get_folder(parser.parse(created_time.value))
        elif isinstance(created_time, str):
            folder = self._get_folder(parser.parse(created_time))
        else:
            folder = self._get_folder(datetime.now(timezone.utc))
        # create document and first version
        document, version = self._create_document(registry, folder)
        # update document data and properties
        version.update(data, properties)
        # store document
        document.get_oid()
        folder[document.oid] = document
        registry.notify(ObjectAddedEvent(version, folder, document.oid))
        # return
        return version

    def import_document(self, oid, data, properties, request=None):
        """Import document from outer ZFiles database"""
        if request is None:
            request = check_request()
        registry = request.registry
        # check required properties
        properties = properties.copy()
        title = properties.get('title')
        application_name = properties.get('application_name')
        created_time = properties.pop('created_time', None)
        if isinstance(created_time, DateTime):
            created_time = parser.parse(created_time.value)
        elif isinstance(created_time, str):
            created_time = parser.parse(created_time)
        if (not oid) or (not title) or (not application_name) or \
                (not created_time) or (data is None):
            raise HTTPBadRequest("Missing arguments")
        if self.oid_prefix and oid.startswith(self.oid_prefix):
            raise HTTPBadRequest("Imported documents shouldn't use the same OID prefix!")
        properties['creator'] = request.principal.id
        # check for existing document
        document = self.get_document(oid)
        if document is not None:
            # add version to existing document
            version = self.update_document(oid, None, data, properties, check_permission=False)
        else:
            # check storage folders
            folder = self._get_folder(created_time)
            document, version = self._create_document(registry, folder)
            version.update(data, properties)
            document.oid = oid
            folder[oid] = document
            registry.notify(ObjectAddedEvent(version, folder, document.oid))
        return version

    @staticmethod
    def find_documents(params, request=None):
        """Find documents matching given params"""
        if not params:
            return
        # check version
        version = params.get('version')
        if version is not None:
            version = int(version)
        filter_versions = (version == -1)
        # create and execute query
        catalog = get_utility(ICatalog)
        query_params = make_query(catalog, params)
        if not query_params:
            return
        if request is None:
            request = check_request()
        results = CatalogResultSet(CatalogQuery(catalog).query(query_params))
        if filter_versions:
            results = unique_iter(map(get_last_version, results))
        else:
            results = map(lambda x: IDocumentVersion(x, None), results)
        yield from filter(lambda x: (x is not None) and
                                    request.has_permission(READ_DOCUMENT_PERMISSION, context=x),
                          results)

    @staticmethod
    def get_document(oid, version=None, status=None):
        """Get existing document from it's OID"""
        if not oid:
            return None
        catalog = get_utility(ICatalog)
        params = Eq(catalog['zfile_oid'], oid)
        # check for version or state
        index = None
        if version:  # check for version number or status
            try:
                index = int(version)  # version number
                status = None
            except ValueError:  # status string
                index = None
                status = version
        if index:
            params = and_(params, Eq(catalog['workflow_version'], index))
        elif status:
            params = and_(params, Eq(catalog['workflow_state'], status))
        for result in ResultSet(CatalogQuery(catalog).query(
                params, sort_index='workflow_version', reverse=True)):
            if version or status:
                return result
            return IWorkflowVersions(result).get_last_versions()[0]
        return None

    def update_document(self, oid, version=None, data=None, properties=None,
                        request=None, check_permission=True):
        # pylint: disable=too-many-arguments
        """Update document data or properties"""
        if not oid:
            return None
        document = self.get_document(oid, version)
        if document is None:
            raise HTTPNotFound()
        if request is None:
            request = check_request()
        if check_permission and \
                not request.has_permission(MANAGE_DOCUMENT_PERMISSION, context=document):
            raise HTTPForbidden()
        if properties is None:
            properties = {}
        if data is not None:
            document_hash = get_hash(data)
            if document_hash == document.hash:
                # unmodified file content
                data = None
                _filename = properties.pop('filename', None)
            else:
                # modified file content, check state and create new version if required
                if request is None:
                    request = check_request()
                state = IWorkflowState(document)
                if state.state != STATE.DRAFT.value:
                    translate = request.localizer.translate
                    workflow_info = IWorkflowInfo(document)
                    document = workflow_info.fire_transition_toward(  # pylint: disable=assignment-from-no-return
                        STATE.DRAFT.value,
                        comment=translate(_("Document content update")),
                        request=request)
                    request.response.status = HTTPCreated.code
        state = document.update(data, properties)
        request.registry.notify(ObjectModifiedEvent(document))
        if state.state == STATE.DELETED.value:
            return None
        return document

    def delete_document(self, oid, request=None):
        """Delete document or version"""
        if not oid:
            return None
        document = self.get_document(oid)
        if document is None:
            raise HTTPNotFound()
        if request is None:
            request = check_request()
        if not request.has_permission(MANAGE_DOCUMENT_PERMISSION, context=document):
            raise HTTPForbidden()
        folder = get_parent(document, IDocumentFolder)
        del folder[document.oid]
        return document


@implementer(IDocumentContainerRoles)
class DocumentContainerRoles(ProtectedObjectRoles):
    """Document container roles"""

    application_managers = RolePrincipalsFieldProperty(
        IDocumentContainerRoles['application_managers'])

    documents_creators = RolePrincipalsFieldProperty(
        IDocumentContainerRoles['documents_creators'])

    documents_managers = RolePrincipalsFieldProperty(
        IDocumentContainerRoles['documents_managers'])

    documents_readers = RolePrincipalsFieldProperty(
        IDocumentContainerRoles['documents_readers'])


@adapter_config(required=IDocumentContainer,
                provides=IDocumentContainerRoles)
def document_container_roles_adapter(context):
    """Document container roles adapter"""
    return DocumentContainerRoles(context)


@adapter_config(required=IDocumentContainer,
                provides=IRolesPolicy)
class DocumentContainerRolesPolicy(ContextAdapter):
    """Document container roles policy"""

    roles_interface = IDocumentContainerRoles
    weight = 10


@adapter_config(name='pyams_zfiles.container',
                required=ISiteRoot,
                provides=ISublocations)
class DocumentContainerSublocation(ContextAdapter):
    """Site root document container sub-location adapter"""

    def sublocations(self):  # pylint: disable=no-self-use
        """Document container"""
        container = query_utility(IDocumentContainer)
        if container is not None:
            yield container
