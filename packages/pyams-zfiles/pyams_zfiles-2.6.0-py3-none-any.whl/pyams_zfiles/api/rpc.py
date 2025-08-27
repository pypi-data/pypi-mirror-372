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

"""PyAMS_zfiles.api.rpc module

This module defines features which are common to all RPC APIs.
"""

import base64
from xmlrpc.client import Binary

from pyramid_rpc.jsonrpc import jsonrpc_method
from pyramid_rpc.xmlrpc import xmlrpc_method

from pyams_file.interfaces.thumbnail import IThumbnails
from pyams_utils.registry import get_utility
from pyams_utils.rpc import RPC_FORBIDDEN, RPC_OBJECT_NOT_FOUND, RPC_SERVICE_UNAVAILABLE, \
    raise_rpc_exception
from pyams_workflow.interfaces import IWorkflowState, IWorkflowVersions
from pyams_zfiles.interfaces import CREATE_DOCUMENT_PERMISSION, CREATE_DOCUMENT_WITH_OWNER_PERMISSION, \
    DEFAULT_CONFIGURATION_NAME, IDocumentContainer, IDocumentSynchronizer, JSONRPC_ENDPOINT, MANAGE_DOCUMENT_PERMISSION, \
    READ_DOCUMENT_PERMISSION, STATE, SYNCHRONIZE_PERMISSION, XMLRPC_ENDPOINT


__docformat__ = 'restructuredtext'


@jsonrpc_method(endpoint=JSONRPC_ENDPOINT,
                method='findFiles',
                require_csrf=False)
@xmlrpc_method(endpoint=XMLRPC_ENDPOINT,
               method='findFiles',
               require_csrf=False)
def find_files(request, properties, fields=None):  # pylint: disable=unused-argument
    """Search documents through RPC"""
    container = get_utility(IDocumentContainer)
    return list(map(lambda x: x.to_json(fields),
                    container.find_documents(properties)))


@jsonrpc_method(endpoint=JSONRPC_ENDPOINT,
                method='uploadFile',
                require_csrf=False)
@xmlrpc_method(endpoint=XMLRPC_ENDPOINT,
               method='uploadFile',
               require_csrf=False)
def upload_file(request, data, properties):
    """Create new document through RPC"""
    container = get_utility(IDocumentContainer)
    if not request.has_permission(CREATE_DOCUMENT_PERMISSION, context=container):
        raise_rpc_exception(request, RPC_FORBIDDEN)
    if isinstance(data, Binary):
        data = data.data
    else:
        data = base64.b64decode(data)
    document = container.add_document(data, properties, request)
    return document.oid


@jsonrpc_method(endpoint=JSONRPC_ENDPOINT,
                method='synchronize',
                require_csrf=False)
@xmlrpc_method(endpoint=XMLRPC_ENDPOINT,
               method='synchronize',
               require_csrf=False)
def synchronize(request, imported=None, deleted=None,
                configuration_name=DEFAULT_CONFIGURATION_NAME):
    """Synchronize documents to remote container"""
    container = get_utility(IDocumentContainer)
    synchronizer = IDocumentSynchronizer(container)
    configuration = synchronizer.get(configuration_name)
    if configuration is None:
        raise_rpc_exception(request, RPC_OBJECT_NOT_FOUND,
                            data={'context': "can't find requested configuration"})
    if not configuration.enabled:
        raise_rpc_exception(request, RPC_SERVICE_UNAVAILABLE,
                            data={'context': "requested configuration is disabled"})
    if not request.has_permission(SYNCHRONIZE_PERMISSION, context=configuration):
        raise_rpc_exception(request, RPC_FORBIDDEN,
                            data={'context': "access to requested configuration is forbidden"})
    return synchronizer.synchronize_all(imported, deleted, request, configuration)


@jsonrpc_method(endpoint=JSONRPC_ENDPOINT,
                method='importFile',
                require_csrf=False)
@xmlrpc_method(endpoint=XMLRPC_ENDPOINT,
               method='importFile',
               require_csrf=False)
def import_file(request, oid, data, properties):
    """Import document from outer ZFiles database through RPC"""
    container = get_utility(IDocumentContainer)
    if not request.has_permission(CREATE_DOCUMENT_WITH_OWNER_PERMISSION, context=container):
        raise_rpc_exception(request, RPC_FORBIDDEN)
    if isinstance(data, Binary):
        data = data.data
    else:
        data = base64.b64decode(data)
    document = container.import_document(oid, data, properties, request)
    return document.oid


def get_document(request, oid, version=None, status=None, permission=READ_DOCUMENT_PERMISSION):
    """Get document matching given OID and version"""
    container = get_utility(IDocumentContainer)
    document = container.get_document(oid, version, status)
    if document is None:
        raise_rpc_exception(request, RPC_OBJECT_NOT_FOUND)
    if permission and not request.has_permission(permission, context=document):
        raise_rpc_exception(request, RPC_FORBIDDEN)
    return document


@jsonrpc_method(endpoint=JSONRPC_ENDPOINT,
                method='canReadFile',
                require_csrf=False)
@xmlrpc_method(endpoint=XMLRPC_ENDPOINT,
               method='canReadFile',
               require_csrf=False)
def can_read(request, oid, version=None, status=None):
    """Check read access on document"""
    document = get_document(request, oid, version, status, permission=None)
    return bool(request.has_permission(READ_DOCUMENT_PERMISSION, context=document))


@jsonrpc_method(endpoint=JSONRPC_ENDPOINT,
                method='canWriteFile',
                require_csrf=False)
@xmlrpc_method(endpoint=XMLRPC_ENDPOINT,
               method='canWriteFile',
               require_csrf=False)
def can_write(request, oid, version=None, status=None):
    """Check write access on document"""
    document = get_document(request, oid, version, status, permission=None)
    return bool(request.has_permission(MANAGE_DOCUMENT_PERMISSION, context=document))


@jsonrpc_method(endpoint=JSONRPC_ENDPOINT,
                method='getFileProperties',
                require_csrf=False)
@xmlrpc_method(endpoint=XMLRPC_ENDPOINT,
               method='getFileProperties',
               require_csrf=False)
def get_file_properties(request, oid, fields=None, version=None, status=None, with_data=False):
    # pylint: disable=too-many-arguments
    """Get document properties"""
    document = get_document(request, oid, version, status)
    result = document.to_json(fields)
    if with_data:
        if request.content_type.startswith('text/xml'):
            result['data'] = Binary(document.data.data)
        else:
            result['data'] = base64.b64encode(document.data.data).decode()
    return result


@jsonrpc_method(endpoint=JSONRPC_ENDPOINT,
                method='setFileProperties',
                require_csrf=False)
@xmlrpc_method(endpoint=XMLRPC_ENDPOINT,
               method='setFileProperties',
               require_csrf=False)
def set_file_properties(request, oid, properties, version=None):
    """Set document properties"""
    container = get_utility(IDocumentContainer)
    document = container.update_document(oid, version, properties=properties, request=request)
    if document is None:
        return None
    state = IWorkflowState(document)
    return {
        'version': state.version_id
    }


@jsonrpc_method(endpoint=JSONRPC_ENDPOINT,
                method='getFileData',
                require_csrf=False)
@xmlrpc_method(endpoint=XMLRPC_ENDPOINT,
               method='getFileData',
               require_csrf=False)
def get_file_data(request, oid, version=None, status=None):
    """Get document data"""
    document = get_document(request, oid, version, status)
    if request.content_type.startswith('text/xml'):
        data = Binary(document.data.data)
    else:
        data = base64.b64encode(document.data.data).decode()
    return {
        'data': data
    }


@jsonrpc_method(endpoint=JSONRPC_ENDPOINT,
                method='setFileData',
                require_csrf=False)
@xmlrpc_method(endpoint=XMLRPC_ENDPOINT,
               method='setFileData',
               require_csrf=False)
def set_file_data(request, oid, data, properties=None, version=None):
    """Set document data"""
    container = get_utility(IDocumentContainer)
    if isinstance(data, Binary):
        data = data.data
    else:
        data = base64.b64decode(data)
    document = container.update_document(oid, version, data, properties, request)
    if document is None:
        return None
    state = IWorkflowState(document)
    return {
        'version': state.version_id
    }


@jsonrpc_method(endpoint=JSONRPC_ENDPOINT,
                method='getFileVersions',
                require_csrf=False)
@xmlrpc_method(endpoint=XMLRPC_ENDPOINT,
               method='getFileVersions',
               require_csrf=False)
def get_file_versions(request, oid, fields=None):
    """Get all document versions properties"""
    document = get_document(request, oid)
    versions = IWorkflowVersions(document)
    result = []
    for version in versions.get_versions(sort=True):
        result.append(version.to_json(fields))
    return result


@jsonrpc_method(endpoint=JSONRPC_ENDPOINT,
                method='archiveFile',
                require_csrf=False)
@xmlrpc_method(endpoint=XMLRPC_ENDPOINT,
               method='archiveFile',
               require_csrf=False)
def archive_file(request, oid, version=None):
    """Archive document"""
    document = get_document(request, oid, version, MANAGE_DOCUMENT_PERMISSION)
    document.update_status({
        'status': STATE.ARCHIVED.value
    })


@jsonrpc_method(endpoint=JSONRPC_ENDPOINT,
                method='removeFile',
                require_csrf=False)
@xmlrpc_method(endpoint=XMLRPC_ENDPOINT,
               method='removeFile',
               require_csrf=False)
@jsonrpc_method(endpoint=JSONRPC_ENDPOINT,
                method='deleteFile',
                require_csrf=False)
@xmlrpc_method(endpoint=XMLRPC_ENDPOINT,
               method='deleteFile',
               require_csrf=False)
def delete_file(request, oid):  # pylint: disable=unused-argument
    """Delete document"""
    container = get_utility(IDocumentContainer)
    container.delete_document(oid)
    return {
        'oid': oid,
        'status': 'deleted'
    }


@jsonrpc_method(endpoint=JSONRPC_ENDPOINT,
                method='getDisplay',
                require_csrf=False)
@xmlrpc_method(endpoint=XMLRPC_ENDPOINT,
               method='getDisplay',
               require_csrf=False)
def get_display(request, oid, display, version=None, status=None):
    """Get document image display"""
    document = get_document(request, oid, version, status)
    thumbnails = IThumbnails(document.data, None)
    if thumbnails is None:
        return None
    thumbnail = thumbnails.get_thumbnail(display)  # pylint: disable=assignment-from-no-return
    result = {
        'content_type': thumbnail.content_type,
        'image_size': thumbnail.image_size
    }
    if request.content_type.startswith('text/xml'):
        result['data'] = Binary(thumbnail.data)
    else:
        result['data'] = base64.b64encode(thumbnail.data)
    return result
