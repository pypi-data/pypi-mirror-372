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

"""PyAMS_zfiles.zmi.document module

This module provides management views for documents.
"""

from zope.interface import Interface

from pyams_form.browser.textlines import TextLinesFieldWidget
from pyams_form.field import Fields
from pyams_form.interfaces.form import IForm
from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_skin.interfaces.view import IModalPage
from pyams_utils.adapter import adapter_config
from pyams_utils.registry import get_utility
from pyams_utils.traversing import get_parent
from pyams_utils.url import absolute_url
from pyams_viewlet.viewlet import viewlet_config
from pyams_zfiles.interfaces import IDocumentContainer, IDocumentVersion, READ_DOCUMENT_PERMISSION
from pyams_zfiles.zmi.properties import PropertiesFieldWidget
from pyams_zmi.form import AdminDisplayForm
from pyams_zmi.interfaces import IAdminLayer, IObjectLabel, IPageTitle
from pyams_zmi.interfaces.form import IFormTitle
from pyams_zmi.interfaces.table import ITableElementEditor
from pyams_zmi.interfaces.viewlet import IContentManagementMenu
from pyams_zmi.table import TableElementEditor
from pyams_zmi.utils import get_object_label
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem

__docformat__ = 'restructuredtext'

from pyams_zfiles import _  # pylint: disable=ungrouped-imports


@adapter_config(required=IDocumentVersion,
                provides=IObjectLabel)
def document_version_label(context):
    """Document version label getter"""
    return f'{context.title} ({context.oid})'


@adapter_config(required=IDocumentVersion,
                provides=IPageTitle)
def document_version_title(context):
    """Document version title getter"""
    return context.title


@adapter_config(required=(IDocumentVersion, IAdminLayer, Interface),
                provides=ITableElementEditor)
class DocumentTableEditor(TableElementEditor):
    """Document table editor"""

    view_name = 'admin#properties.html'
    modal_target = False


@viewlet_config(name='properties.menu', context=IDocumentVersion, layer=IAdminLayer,
                manager=IContentManagementMenu, weight=10,
                permission=READ_DOCUMENT_PERMISSION)
class DocumentPropertiesDisplayMenu(NavigationMenuItem):
    """Document properties display menu"""

    label = _("Properties")
    icon_class = 'far fa-id-card'
    href = '#properties.html'


@pagelet_config(name='properties.html', context=IDocumentVersion, layer=IPyAMSLayer,
                permission=READ_DOCUMENT_PERMISSION)
class DocumentPropertiesDisplayForm(AdminDisplayForm):
    """Document properties display form"""

    @property
    def back_url(self):
        """Form back URL getter"""
        container = get_utility(IDocumentContainer)
        return absolute_url(container, self.request, 'admin#search.html')

    back_url_target = None

    legend = _("Document properties")
    label_css_class = 'col-sm-3'
    input_css_class = 'col-sm-9'

    fields = Fields(IDocumentVersion).omit('__parent__', '__name__')
    fields['properties'].widget_factory = PropertiesFieldWidget
    fields['tags'].widget_factory = TextLinesFieldWidget


@adapter_config(required=(IDocumentVersion, IAdminLayer, Interface),
                provides=IPageTitle)
def document_view_title(context, request, view):
    """Base document view title adapter"""
    container = get_parent(context, IDocumentContainer)
    container_label = get_object_label(container, request, view)
    document_label = get_object_label(context, request, view)
    return f'{container_label} <small><small>' \
           f' <i class="px-2 fas fa-chevron-right"></i> ' \
           f'{document_label}</small></small>'


@adapter_config(required=(IDocumentVersion, IAdminLayer, IModalPage),
                provides=IPageTitle)
def document_modal_page_title(context, request, view):
    """Document modal page title"""
    container = get_parent(context, IDocumentContainer)
    return get_object_label(container, request, view)


@adapter_config(required=(IDocumentVersion, IAdminLayer, IForm),
                provides=IFormTitle)
def document_form_title(context, request, view):
    """Document form title adapter"""
    return f'{document_version_title(context)} - {context.application_name}'


@adapter_config(required=(IDocumentVersion, IAdminLayer, IModalPage),
                provides=IFormTitle)
def document_modal_form_title(context, request, view):
    """Document modal view title adapter"""
    return get_object_label(context, request, view)
