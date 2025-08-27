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

"""PyAMS_zfiles.skin.file module

This module defines a custom view for protected files.
"""

from pyramid.httpexceptions import HTTPForbidden
from pyramid.view import view_config

from pyams_file.interfaces import IFile
from pyams_file.skin.view import FileView
from pyams_zfiles.interfaces import READ_DOCUMENT_PERMISSION
from pyams_zfiles.layer import IPyAMSZFilesLayer


__docformat__ = 'restructuredtext'


@view_config(context=IFile,
             request_method=('OPTIONS', 'GET'),
             request_type=IPyAMSZFilesLayer)
def ProtectedFileView(request):  # pylint: disable=invalid-name
    """Protected file view"""
    if (request.method == 'GET') and \
            not request.has_permission(READ_DOCUMENT_PERMISSION, context=request.context):
        raise HTTPForbidden()
    return FileView(request)
