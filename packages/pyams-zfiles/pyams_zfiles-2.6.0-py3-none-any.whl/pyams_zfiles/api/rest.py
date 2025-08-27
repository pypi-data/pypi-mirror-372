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

"""PyAMS_zfiles.api.rest module

This module defines ZFiles REST API.
"""

import base64
import sys

from colander import DateTime, Int, MappingSchema, OneOf, SchemaNode, SequenceSchema, String, drop
from cornice import Service
from cornice.validators import colander_body_validator, colander_validator
from pyramid.httpexceptions import HTTPBadRequest, HTTPCreated, HTTPError, HTTPForbidden, HTTPNotFound, HTTPOk, \
    HTTPServiceUnavailable

from pyams_security.rest import check_authentication, check_cors_origin, set_cors_headers
from pyams_utils.dict import merge_dict
from pyams_utils.registry import get_utility, query_utility
from pyams_utils.rest import BaseResponseSchema, DateRangeSchema, FileUploadType, PropertiesMapping, STATUS, \
    StringArraySchema, StringListSchema, http_error, rest_responses
from pyams_zfiles.interfaces import ACCESS_MODE, CREATE_DOCUMENT_PERMISSION, CREATE_DOCUMENT_WITH_OWNER_PERMISSION, \
    DEFAULT_CONFIGURATION_NAME, IDocumentContainer, IDocumentSynchronizer, READ_DOCUMENT_PERMISSION, \
    REST_CONTAINER_ROUTE, REST_DOCUMENT_ROUTE, REST_SYNCHRONIZER_ROUTE, STATE, SYNCHRONIZE_PERMISSION

__docformat__ = 'restructuredtext'

from pyams_zfiles.search import LIST_SEPARATOR


TEST_MODE = sys.argv[-1].endswith('/test')


class FieldsNamesString(MappingSchema):
    """Properties fields names string"""
    fields = SchemaNode(String(),
                        description="List of requested fields names, separated by commas",
                        missing=drop)


class FieldsNamesArray(MappingSchema):
    """Properties fields names array"""
    fields = StringListSchema(description="Array of requested fields names",
                              missing=drop)


class EmptyDocumentInfo(MappingSchema):
    """Empty document schema"""
    title = SchemaNode(String(),
                       description="Document title",
                       missing=drop)
    application_name = SchemaNode(String(),
                                  description="Source application name",
                                  missing=drop)
    filename = SchemaNode(String(),
                          description="File name",
                          missing=drop)
    properties = SchemaNode(PropertiesMapping(),
                            description="Custom document properties",
                            missing=drop)
    tags = StringListSchema(description="List of document tags",
                            missing=drop)
    owner = SchemaNode(String(),
                       description="Current document owner",
                       missing=drop)
    status = SchemaNode(String(),
                        description="Document status",
                        validator=OneOf((STATE.DRAFT.value,
                                         STATE.PUBLISHED.value,
                                         STATE.ARCHIVED.value,
                                         STATE.DELETED.value)),
                        default=STATE.DRAFT.value,
                        missing=drop)
    access_mode = SchemaNode(String(),
                             description="Access mode",
                             validator=OneOf([ACCESS_MODE.PRIVATE.value,
                                              ACCESS_MODE.PROTECTED.value,
                                              ACCESS_MODE.PUBLIC.value]),
                             default=ACCESS_MODE.PRIVATE.value,
                             missing=drop)
    readers = StringListSchema(description="Document readers IDs",
                               missing=drop)
    update_mode = SchemaNode(String(),
                             description="Update mode",
                             validator=OneOf([ACCESS_MODE.PRIVATE.value,
                                              ACCESS_MODE.PROTECTED.value,
                                              ACCESS_MODE.PUBLIC.value]),
                             default=ACCESS_MODE.PRIVATE.value,
                             missing=drop)
    managers = StringListSchema(description="Document managers IDs",
                                missing=drop)


class DocumentInfoWithData(EmptyDocumentInfo):
    """Document data update schema"""
    data = SchemaNode(FileUploadType(),
                      description="Document data; may be provided in Base64 when using JSON",
                      missing=drop)
    filename = SchemaNode(String(),
                          description="File name",
                          missing=drop)


class NewDocumentInfo(DocumentInfoWithData):
    """New document schema"""
    title = SchemaNode(String(),
                       description="Document title")
    application_name = SchemaNode(String(),
                                  description="Source application name")
    filename = SchemaNode(String(),
                          description="Document file name")
    created_time = SchemaNode(String(),
                              description="Document creation timestamp",
                              missing=drop)
    data = SchemaNode(FileUploadType(),
                      description="Document data; may be provided in Base64 when using JSON",
                      missing=drop)


class ImportedDocumentInfo(NewDocumentInfo):
    """Import document schema"""
    created_time = SchemaNode(DateTime(),
                              description="Document creation timestamp")
    owner = SchemaNode(String(),
                       description="Current document owner")


class Document(EmptyDocumentInfo):
    """Document schema"""
    title = SchemaNode(String(),
                       description="Document title")
    application_name = SchemaNode(String(),
                                  description="Source application name")
    filename = SchemaNode(String(),
                          description="File name")
    api = SchemaNode(String(),
                     description="Document base REST API URL")
    oid = SchemaNode(String(),
                     description="Document unique identifier")
    version = SchemaNode(Int(),
                         description="Document version")
    href = SchemaNode(String(),
                      description="Absolute URL of document data file")
    hash = SchemaNode(String(),
                      description="SHA512 hash of document data file")
    filesize = SchemaNode(Int(),
                          description="Document file size")
    content_type = SchemaNode(String(),
                              description="Document content type")
    creator = SchemaNode(String(),
                         description="Document creator principal ID")
    created_time = SchemaNode(DateTime(),
                              description="Document creation timestamp")
    owner = SchemaNode(String(),
                       description="Current document owner")
    updater = SchemaNode(String(),
                         description="Last document updater principal ID")
    updated_time = SchemaNode(DateTime(),
                              description="Last document update timestamp")
    status_updater = SchemaNode(String(),
                                description="Last workflow status updater principal ID")
    status_update_time = SchemaNode(DateTime(),
                                    description="Last document status update timestamp")


class UpdatedDocument(Document):
    """Updated document schema"""
    oid = SchemaNode(String(),
                     description="Document unique identifier")
    status = SchemaNode(String(),
                        description="Document status",
                        validator=OneOf((STATE.DRAFT.value,
                                         STATE.PUBLISHED.value,
                                         STATE.ARCHIVED.value,
                                         STATE.DELETED.value)))
    title = SchemaNode(String(),
                       description="Document title",
                       missing=drop)
    application_name = SchemaNode(String(),
                                  description="Source application name",
                                  missing=drop)
    filename = SchemaNode(String(),
                          description="File name",
                          missing=drop)
    api = SchemaNode(String(),
                     description="Document base REST API URL",
                     missing=drop)
    version = SchemaNode(Int(),
                         description="Document version",
                         missing=drop)
    href = SchemaNode(String(),
                      description="Absolute URL of document data file",
                      missing=drop)
    hash = SchemaNode(String(),
                      description="SHA512 hash of document data file",
                      missing=drop)
    filesize = SchemaNode(Int(),
                          description="Document file size",
                          missing=drop)
    content_type = SchemaNode(String(),
                              description="Document content type",
                              missing=drop)
    creator = SchemaNode(String(),
                         description="Document creator principal ID",
                         missing=drop)
    created_time = SchemaNode(DateTime(),
                              description="Document creation timestamp",
                              missing=drop)
    owner = SchemaNode(String(),
                       description="Current document owner",
                       missing=drop)
    updater = SchemaNode(String(),
                         description="Last document updater principal ID",
                         missing=drop)
    updated_time = SchemaNode(DateTime(),
                              description="Last document update timestamp",
                              missing=drop)
    status_updater = SchemaNode(String(),
                                description="Last workflow status updater principal ID",
                                missing=drop)
    status_update_time = SchemaNode(DateTime(),
                                    description="Last document status update timestamp",
                                    missing=drop)


class DocumentsList(SequenceSchema):
    """Documents list schema"""
    document = Document()


class DocumentsSearchResults(BaseResponseSchema):
    """Documents search results"""
    results = DocumentsList(description="Documents list",
                            missing=drop)


class DocumentSearchQuery(MappingSchema):
    """Document search query"""
    oid = StringListSchema(description="Document unique identifiers",
                           missing=drop)
    version = SchemaNode(Int(),
                         description="Document version",
                         missing=drop)
    title = SchemaNode(String(),
                       description="Document title",
                       missing=drop)
    application_name = SchemaNode(String(),
                                  description="Source application name",
                                  missing=drop)
    hash = SchemaNode(String(),
                      description="SHA512 hash of document data file",
                      missing=drop)
    properties = SchemaNode(PropertiesMapping(),
                            description="Document properties, provided as a mapping",
                            missing=drop)
    tags = StringListSchema(description="Document tags, separated with semicolons",
                            missing=drop)
    status = SchemaNode(String(),
                        description="Document status",
                        validator=OneOf((STATE.DRAFT.value,
                                         STATE.PUBLISHED.value,
                                         STATE.ARCHIVED.value,
                                         STATE.DELETED.value)),
                        default=STATE.DRAFT.value,
                        missing=drop)
    creator = SchemaNode(String(),
                         description="Document creator principal ID",
                         missing=drop)
    created_date = DateRangeSchema(description="Document creation dates range",
                                   missing=drop)
    owner = SchemaNode(String(),
                       description="Current document owner",
                       missing=drop)
    updater = SchemaNode(String(),
                         description="Last document updater principal ID",
                         missing=drop)
    updated_date = DateRangeSchema(description="Document last update dates range",
                                   missing=drop)
    status_updater = SchemaNode(String(),
                                description="Last workflow status updater principal ID",
                                missing=drop)
    status_update_date = DateRangeSchema(description="Last workflow status update dates range",
                                         missing=drop)
    fields = StringListSchema(description="List of requested field names",
                              missing=drop)


class DocumentSearchQueryString(DocumentSearchQuery):
    """Document search query using querystring params"""
    created_date = SchemaNode(String(),
                              description="Document creation dates range in ISO-8601 format, separated by commas; "
                                          "unset values should be replaced by *null*",
                              missing=drop)
    updated_date = SchemaNode(String(),
                              description="Document last update dates range in ISO-8601 format, separated by "
                                          "commas; unset values should be replaced by *null*",
                              missing=drop)
    status_update_date = SchemaNode(String(),
                                    description="Last workflow status update dates range in ISO-8601 format, separated "
                                                "by commas; unset values should be replaced by *null*",
                                    missing=drop)
    tags = SchemaNode(StringArraySchema(),
                      description="List of documents tags, separated by commas",
                      missing=drop)
    fields = SchemaNode(String(),
                        description="List of requested field names, separated by commas",
                        missing=drop)


class DocumentsSynchronizeInfo(MappingSchema):
    """Documents synchronize schema"""
    imported = StringListSchema(description="List of documents to import in remote documents "
                                            "container",
                                missing=drop)
    deleted = StringListSchema(description="List of documents to remove from remote documents "
                                           "container",
                               missing=drop)
    configuration_name = SchemaNode(String(),
                                    description="Selected configuration name",
                                    missing=drop)


class DeletedDocumentInfo(MappingSchema):
    """Deleted document schema"""
    oid = SchemaNode(String(),
                     description="Document unique identifier")
    status = SchemaNode(String(),
                        description="Document status",
                        validator=OneOf((STATE.DRAFT.value,
                                         STATE.PUBLISHED.value,
                                         STATE.ARCHIVED.value,
                                         STATE.DELETED.value)))


#
# Documents container service
#

container_service = Service(name=REST_CONTAINER_ROUTE,
                            pyramid_route=REST_CONTAINER_ROUTE,
                            description="ZFiles container service")


@container_service.options(validators=(check_cors_origin, set_cors_headers))
def container_options(request):  # pylint: disable=unused-argument
    """Container options endpoint"""
    return ''


class DocumentSearchRequest(MappingSchema):
    """Documents container search schema"""
    querystring = DocumentSearchQueryString(missing=drop)
    body = DocumentSearchQuery(missing=drop)


class DocumentSearchResponse(MappingSchema):
    """Documents container search response"""
    body = DocumentsSearchResults()


container_get_responses = rest_responses.copy()
container_get_responses[HTTPOk.code] = DocumentSearchResponse(
    description="Container documents search results")


@container_service.get(content_type=('application/json', 'multipart/form-data'),
                       schema=DocumentSearchRequest(),
                       validators=(check_cors_origin, check_authentication,
                                   colander_validator, set_cors_headers),
                       response_schemas=container_get_responses)
def find_documents(request):
    """Find documents matching specified properties"""
    if TEST_MODE:
        properties = request.params.copy()
    else:
        properties = {}
        merge_dict(request.validated.get('querystring', {}), properties)
        merge_dict(request.validated.get('body', {}), properties)
    fields = properties.pop('fields', None)
    if isinstance(fields, str):
        fields = set(fields.split(LIST_SEPARATOR))
    container = get_utility(IDocumentContainer)
    return {
        'status': STATUS.SUCCESS.value,
        'results': list(map(lambda x: x.to_json(fields),
                            container.find_documents(properties)))
    }


class ContainerCreationResponse(MappingSchema):
    """Container upload response"""
    body = Document()


container_post_responses = rest_responses.copy()
container_post_responses[HTTPOk.code] = ContainerCreationResponse(
    description="Documents container creation result")


@container_service.post(content_type=('application/json', 'multipart/form-data'),
                        schema=NewDocumentInfo(),
                        validators=(check_cors_origin, check_authentication,
                                    colander_body_validator, set_cors_headers),
                        require_csrf=False)
def create_document(request):
    """Create new ZFiles document using multipart/form-data encoding"""
    container = query_utility(IDocumentContainer)
    if container is None:
        return http_error(request, HTTPServiceUnavailable)
    if not request.has_permission(CREATE_DOCUMENT_PERMISSION, context=container):
        return http_error(request, HTTPForbidden)
    properties = request.params.copy() if TEST_MODE else request.validated.copy()
    if request.headers.get('Content-Type').startswith('multipart/form-data'):
        properties['data'] = request.params.get('data')
    else:
        properties['data'] = base64.b64decode(request.json.get('data'))
    data = properties.pop('data', None)
    document = container.add_document(data, properties, request)
    result = document.to_json()
    request.response.status = HTTPCreated.code
    request.response.headers['location'] = result['api']
    return result


#
# Documents synchronizer service
#

synchronizer_service = Service(name=REST_SYNCHRONIZER_ROUTE,
                               pyramid_route=REST_SYNCHRONIZER_ROUTE,
                               description="ZFiles synchronizer service")


@synchronizer_service.options(validators=(check_cors_origin, set_cors_headers))
def synchronizer_options(request):  # pylint: disable=unused-argument
    """Synchronizer OPTIONS verb handler"""
    return ''


class SynchronizerPutResults(MappingSchema):
    """Synchronizer request results"""


class SynchronizerPutResponse(MappingSchema):
    """Synchronizer request response"""
    body = SynchronizerPutResults(description="Synchronization result for each document")


synchronizer_put_responses = rest_responses.copy()
synchronizer_put_responses[HTTPOk.code] = SynchronizerPutResponse(
    description="Result of synchronization")


@synchronizer_service.put(content_type=('application/json', 'multipart/form-data'),
                          schema=DocumentsSynchronizeInfo(),
                          validators=(check_cors_origin, check_authentication,
                                      colander_body_validator, set_cors_headers),
                          require_csrf=False,
                          response_schemas=synchronizer_put_responses)
def synchronizer_put(request):
    """Document synchronizer request"""
    params = request.params.copy() if TEST_MODE else request.validated.copy()
    container = get_utility(IDocumentContainer)
    synchronizer = IDocumentSynchronizer(container)
    configuration_name = params.get('configuration_name', DEFAULT_CONFIGURATION_NAME)
    configuration = synchronizer.get(configuration_name)
    if configuration is None:
        return http_error(request, HTTPNotFound)
    if not configuration.enabled:
        return http_error(request, HTTPServiceUnavailable)
    if not request.has_permission(SYNCHRONIZE_PERMISSION, context=configuration):
        return http_error(request, HTTPForbidden)
    return synchronizer.synchronize_all(params.get('imported'), params.get('deleted'),
                                        request, configuration)


#
# Document service
#

document_service = Service(name=REST_DOCUMENT_ROUTE,
                           pyramid_route=REST_DOCUMENT_ROUTE,
                           description="ZFiles document service")


@document_service.options(validators=(check_cors_origin, set_cors_headers))
def document_options(request):  # pylint: disable=unused-argument
    """Document OPTIONS verb handler"""
    return ''


def get_ids(request):
    """Get document ID and version from request path"""
    oid = request.matchdict['oid']
    if not oid:
        raise HTTPBadRequest()
    version = request.matchdict['version']
    if version:
        version = version[0]
    return oid, version or None


class DocumentGetRequest(MappingSchema):
    """Document getter request"""
    querystring = FieldsNamesString(missing=drop)
    body = FieldsNamesArray(missing=drop)


class DocumentGetResponse(MappingSchema):
    """Document getter response"""
    body = Document()


document_get_responses = rest_responses.copy()
document_get_responses[HTTPOk.code] = DocumentGetResponse(
    description="Document properties")


@document_service.get(schema=DocumentGetRequest(),
                      validators=(check_cors_origin, check_authentication,
                                  colander_validator, set_cors_headers),
                      response_schemas=document_get_responses)
def get_document(request):
    """Retrieve existing document information"""
    container = get_utility(IDocumentContainer)
    document = container.get_document(*get_ids(request))
    if document is None:
        return http_error(request, HTTPNotFound)
    if not request.has_permission(READ_DOCUMENT_PERMISSION, context=document):
        return http_error(request, HTTPForbidden)
    if TEST_MODE:
        params = request.params
    else:
        params = request.validated.get('body') or request.validated.get('querystring') or {}
    fields = params.get('fields')
    if isinstance(fields, str):
        fields = set(fields.split(LIST_SEPARATOR))
    return document.to_json(fields)


class DocumentImportResponse(MappingSchema):
    """Document import response"""
    body = Document()


document_import_responses = rest_responses.copy()
document_import_responses[HTTPOk.code] = DocumentImportResponse(
    description="Imported document properties")


@document_service.post(content_type=('application/json', 'multipart/form-data'),
                       schema=ImportedDocumentInfo(),
                       validators=(check_cors_origin, check_authentication,
                                   colander_body_validator, set_cors_headers),
                       require_csrf=False,
                       response_schemas=document_import_responses)
def import_document(request):
    """Import document from other ZFiles database"""
    container = get_utility(IDocumentContainer)
    if not request.has_permission(CREATE_DOCUMENT_WITH_OWNER_PERMISSION, context=container):
        raise HTTPForbidden()
    properties = request.params.copy() if TEST_MODE else request.validated.copy()
    if request.headers.get('Content-Type').startswith('multipart/form-data'):
        properties['data'] = request.params.get('data')
    else:
        properties['data'] = base64.b64decode(request.json.get('data'))
    oid = request.matchdict['oid']
    data = properties.pop('data', None)
    try:
        document = container.import_document(oid, data, properties, request)
    except HTTPError as error:
        return http_error(request, error)
    result = document.to_json()
    request.response.status = HTTPCreated.code
    request.response.headers['location'] = result['api']
    return result


class DocumentUpdateResponse(MappingSchema):
    """Document update response"""
    body = UpdatedDocument()


document_update_responses = rest_responses.copy()
document_update_responses[HTTPOk.code] = DocumentUpdateResponse(
    description="Updated document properties")


@document_service.patch(content_type=('application/json', 'multipart/form-data'),
                        schema=EmptyDocumentInfo(),
                        validators=(check_cors_origin, check_authentication,
                                    colander_body_validator, set_cors_headers),
                        require_csrf=False,
                        response_schemas=document_update_responses)
def patch_document(request):
    """Update existing document properties, excluding file data"""
    oid, version = get_ids(request)
    container = get_utility(IDocumentContainer)
    properties = request.params.copy() if TEST_MODE else request.validated.copy()
    try:
        document = container.update_document(oid, version, properties=properties, request=request)
    except HTTPError as error:
        return http_error(request, error)
    if document is None:
        return {
            'oid': oid,
            'status': STATE.DELETED.value
        }
    return document.to_json()


class DocumentDataUpdateResponse(MappingSchema):
    """Document data update response"""
    body = UpdatedDocument()


document_data_update_responses = rest_responses.copy()
document_data_update_responses[HTTPOk.code] = DocumentDataUpdateResponse(
    description="Updated document properties")


@document_service.put(content_type=('application/json', 'multipart/form-data'),
                      schema=DocumentInfoWithData(),
                      validators=(check_cors_origin, check_authentication,
                                  colander_body_validator, set_cors_headers),
                      require_csrf=False,
                      response_schemas=document_data_update_responses)
def put_document(request):
    """Update existing document content"""
    oid, version = get_ids(request)
    container = get_utility(IDocumentContainer)
    properties = request.params.copy() if TEST_MODE else request.validated.copy()
    if request.headers.get('Content-Type').startswith('multipart/form-data'):
        properties['data'] = request.params.get('data')
    else:
        properties['data'] = base64.b64decode(request.json.get('data'))
    data = properties.pop('data')
    try:
        document = container.update_document(oid, version, data, properties, request)
    except HTTPError as error:
        return http_error(request, error)
    if document is None:
        return {
            'oid': oid,
            'status': STATE.DELETED.value
        }
    return document.to_json()


class DocumentDeleteResponse(MappingSchema):
    """Deleted document response"""
    body = DeletedDocumentInfo()


document_delete_responses = rest_responses.copy()
document_delete_responses[HTTPOk.code] = DocumentDeleteResponse(
    description="Delete document properties")


@document_service.delete(require_csrf=False,
                         validators=(check_cors_origin, check_authentication,
                                     set_cors_headers),
                         response_schemas=document_delete_responses)
def delete_document(request):
    """Delete existing document content"""
    oid, _version = get_ids(request)
    container = get_utility(IDocumentContainer)
    try:
        container.delete_document(oid)
    except HTTPError as error:
        return http_error(request, error)
    return {
        'oid': oid,
        'status': STATE.DELETED.value
    }
