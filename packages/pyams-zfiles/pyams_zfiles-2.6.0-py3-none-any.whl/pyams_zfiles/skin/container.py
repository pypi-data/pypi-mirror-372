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

"""PyAMS_zfiles.skin.container module

This module is used to automatically apply a custom skin layer on
request during traversal, so that files are correctly protected
from unauthorized access.
"""

from pyramid.events import subscriber
from zope.traversing.interfaces import IBeforeTraverseEvent

from pyams_layer.skin import apply_skin
from pyams_zfiles.interfaces import IDocumentContainer, PYAMS_ZFILES_SKIN_NAME


__docformat__ = 'restructuredtext'


@subscriber(IBeforeTraverseEvent, context_selector=IDocumentContainer)
def handle_document_container_before_traverse(event):
    """Apply custom ZFiles skin on traversing"""
    apply_skin(event.request, PYAMS_ZFILES_SKIN_NAME)
