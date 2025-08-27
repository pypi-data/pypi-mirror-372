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

"""PyAMS_zfiles.api.graph module

This module provides ZFiles GraphQL API.
"""

import base64

from graphene import Field, Int, JSONString, List, Mutation, ObjectType, Schema, String
from pyramid.httpexceptions import HTTPBadRequest, HTTPForbidden, HTTPNotFound
from pyramid.view import view_config

from pyams_utils.registry import get_utility
from pyams_zfiles.interfaces import CREATE_DOCUMENT_PERMISSION, \
    CREATE_DOCUMENT_WITH_OWNER_PERMISSION, GRAPHQL_API_ROUTE, IDocumentContainer, \
    READ_DOCUMENT_PERMISSION


__docformat__ = 'restructuredtext'

from pyams_zfiles import _


#
# GraphQL types
#

class Properties(JSONString):
    """Custom properties mapping type"""

    @staticmethod
    def serialize(dt):
        return dt


class DateRange(List):
    """Dates range schema"""


#
# Document schemas
#

class DocumentSchema(ObjectType):
    """Base document object type"""
    # read-write attributes
    title = String(description=_("Document title"))
    application_name = String(description=_("Source application name"))
    filename = String(description=_("File name"))
    properties = Properties(description=_("Document custom properties"))
    tags = List(String, description=_("Document tags"))
    status = String(description=_("Document workflow state"))
    owner = String(description=_("Current document owner"))
    access_mode = String(description=_("Document access mode"))
    readers = List(String, description=_("Document readers IDs"))
    update_mode = String(description=_("Document update mode"))
    managers = List(String, description=_("Document managers IDs"))
    # read-only attributes
    api = String(description=_("Document base REST API URL"))
    oid = String(description=_("Document unique identifier"))
    href = String(description=_("Absolute URL of document data file"))
    hash = String(description=_("SHA512 hash of document data file"))
    filesize = String(description=_("Document file size"))
    content_type = String(description=_("Document content type"))
    version = Int(description=_("Document version"))
    creator = String(description=_("Document creator principal ID"))
    created_time = String(description=_("Document creation timestamp"))
    updater = String(description=_("Last document updater principal ID"))
    updated_time = String(description=_("Last document update timestamp"))
    status_updater = String(description=_("Last document status updater principal ID"))
    status_update_time = String(description=_("Last document status update timestamp"))


class DocumentDataSchema(ObjectType):
    """Document data update schema"""
    data = String(description=_("Document data in Base64 encoding"))


#
# Document GraphQL queries
#

class DocumentQuery(ObjectType):
    """Document GraphQL query"""

    # documents search
    search = Field(List(DocumentSchema),
                   oid=DocumentSchema.oid,
                   version=DocumentSchema.version,
                   title=DocumentSchema.title,
                   application_name=DocumentSchema.application_name,
                   hash=DocumentSchema.hash,
                   properties=String(description=_("Properties query string")),
                   tags=DocumentSchema.tags,
                   status=DocumentSchema.status,
                   creator=DocumentSchema.creator,
                   created_date=List(String,
                                     description=_("Document creation dates range")),
                   owner=DocumentSchema.owner,
                   updater=DocumentSchema.updater,
                   updated_date=List(String,
                                     description=_("Document last modification dates range")),
                   status_updater=DocumentSchema.status_updater,
                   status_update_date=List(String,
                                           description=_("Document last workflow update dates "
                                                         "range")))

    def resolve_search(self, info, **params):  # pylint: disable=no-self-use
        """Resolve documents search"""
        container = get_utility(IDocumentContainer)
        return list((
            document.to_json()
            for document in container.find_documents(params, request=info.context)
        ))

    # document getter
    document = Field(DocumentSchema,
                     oid=String(description=_("Document unique identifier"),
                                required=True),
                     version=Int(description=_("Document version")),
                     status=String(description=_("Document status")))

    def resolve_document(self, info, oid, version=None, status=None):  # pylint: disable=no-self-use
        """Resolve document properties"""
        container = get_utility(IDocumentContainer)
        document = container.get_document(oid, version, status)
        if document is None:
            raise HTTPNotFound()
        request = info.context
        if not request.has_permission(READ_DOCUMENT_PERMISSION, context=document):
            raise HTTPForbidden()
        return document.to_json(request=request)

    # document data getter
    data = Field(String,
                 oid=String(description=_("Document unique identifier"),
                            required=True),
                 version=Int(description=_("Document version")),
                 status=String(description=_("Document status")))

    def resolve_data(self, info, oid, version=None, status=None):  # pylint: disable=no-self-use
        """Resolve document data"""
        container = get_utility(IDocumentContainer)
        document = container.get_document(oid, version, status)
        if document is None:
            raise HTTPNotFound()
        request = info.context
        if not request.has_permission(READ_DOCUMENT_PERMISSION, context=document):
            raise HTTPForbidden()
        return base64.b64encode(document.data.data).decode()


#
# Document creation mutation
#

class CreateDocument(Mutation):
    """Document creation mutation"""

    class Arguments:
        """Document creation arguments"""
        title = String(description=_("Document title"),
                       required=True)
        application_name = String(description=_("Source application"),
                                  required=True)
        filename = String(description=_("File name"),
                          required=True)
        data = String(description=_("Document data in Base64 encoding"),
                      required=True)
        properties = DocumentSchema.properties
        tags = DocumentSchema.tags
        status = DocumentSchema.status
        access_mode = DocumentSchema.access_mode
        readers = DocumentSchema.readers
        update_mode = DocumentSchema.update_mode
        managers = DocumentSchema.managers

    document = Field(DocumentSchema)

    def mutate(self, info, **properties):  # pylint: disable=no-self-use
        """Create new document"""
        request = info.context
        container = get_utility(IDocumentContainer)
        if not request.has_permission(CREATE_DOCUMENT_PERMISSION, context=container):
            raise HTTPForbidden()
        data = base64.b64decode(properties.pop('data', None))
        document = container.add_document(data, properties, request=request)
        return CreateDocument(document=document.to_json())


class ImportDocument(Mutation):
    """Document import mutation"""

    class Arguments:
        """Document creation arguments"""
        oid = String(description=_("Document unique identifier"),
                     required=True)
        title = String(description=_("Document title"),
                       required=True)
        application_name = String(description=_("Source application"),
                                  required=True)
        filename = String(description=_("Document file name"),
                          required=True)
        data = String(description=_("Document data in Base64 encoding"),
                      required=True)
        owner = String(description=_("Current document owner"),
                       required=True)
        created_time = String(description=_("Document creation date"),
                              required=True)
        properties = DocumentSchema.properties
        tags = DocumentSchema.tags
        status = DocumentSchema.status
        access_mode = DocumentSchema.access_mode
        readers = DocumentSchema.readers
        update_mode = DocumentSchema.update_mode
        managers = DocumentSchema.managers

    document = Field(DocumentSchema)

    def mutate(self, info, **properties):  # pylint: disable=no-self-use
        """Create new document"""
        request = info.context
        container = get_utility(IDocumentContainer)
        if not request.has_permission(CREATE_DOCUMENT_WITH_OWNER_PERMISSION, context=container):
            raise HTTPForbidden()
        oid = properties.pop('oid')
        data = base64.b64decode(properties.pop('data', None))
        document = container.import_document(oid, data, properties, request=request)
        return ImportDocument(document=document.to_json())


class UpdateDocument(Mutation):
    """Document update mutation"""

    class Arguments:
        """Document update arguments"""
        oid = String(required=True)
        version = DocumentSchema.version
        title = DocumentSchema.title
        application_name = DocumentSchema.application_name
        filename = DocumentSchema.filename
        data = DocumentDataSchema.data
        properties = DocumentSchema.properties
        tags = DocumentSchema.tags
        status = DocumentSchema.status
        access_mode = DocumentSchema.access_mode
        readers = DocumentSchema.readers
        update_mode = DocumentSchema.update_mode
        managers = DocumentSchema.managers

    document = Field(DocumentSchema)

    def mutate(self, info, **properties):  # pylint: disable=no-self-use
        """Update existing document"""
        oid = properties.pop('oid')
        version = properties.pop('version', None)
        data = properties.pop('data', None)
        if data:
            data = base64.b64decode(data)
        container = get_utility(IDocumentContainer)
        document = container.update_document(oid, version, data, properties,
                                             request=info.context)
        if document is None:
            return UpdateDocument(document={
                'oid': oid,
                'status': 'deleted'
            })
        return UpdateDocument(document=document.to_json())


class DeleteDocument(Mutation):
    """Document delete mutation"""

    class Arguments:
        """Document delete arguments"""
        oid = String(required=True)

    document = Field(DocumentSchema)

    def mutate(self, info, oid):  # pylint: disable=no-self-use,unused-argument
        """Delete existing document"""
        container = get_utility(IDocumentContainer)
        container.delete_document(oid)
        return DeleteDocument(document={
            'oid': oid,
            'status': 'deleted'
        })


#
# Document mutations
#

class DocumentMutations(ObjectType):
    """Document mutations"""
    create_document = CreateDocument.Field()
    import_document = ImportDocument.Field()
    update_document = UpdateDocument.Field()
    delete_document = DeleteDocument.Field()


#
# Document GraphQL schema
#

schema = Schema(query=DocumentQuery,
                mutation=DocumentMutations)


@view_config(route_name=GRAPHQL_API_ROUTE, renderer='json', require_csrf=False)
def graphql_view(request):
    """GraphQL API view"""
    query = request.json_body.get('query')
    if not query:
        raise HTTPBadRequest("Missing request")
    result = schema.execute(query,
                            context=request,
                            variables=request.json_body.get('variables'))
    if result.errors:
        raise HTTPBadRequest(', '.join((str(error) for error in result.errors)))
    return result.data
