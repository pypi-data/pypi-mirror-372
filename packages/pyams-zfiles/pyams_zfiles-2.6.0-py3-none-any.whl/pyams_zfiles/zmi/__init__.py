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

"""PyAMS_zfiles.zmi module

This module defines base documents container management views.
"""

from zope.interface import Interface

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_layer.interfaces import IPyAMSLayer
from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_site.interfaces import ISiteRoot
from pyams_skin.interfaces.view import IModalPage
from pyams_skin.interfaces.viewlet import IBreadcrumbItem
from pyams_utils.adapter import adapter_config
from pyams_utils.registry import get_utility, query_utility
from pyams_utils.url import absolute_url
from pyams_viewlet.manager import viewletmanager_config
from pyams_viewlet.viewlet import viewlet_config
from pyams_zfiles.interfaces import IDocumentContainer, MANAGE_APPLICATION_PERMISSION, \
    MANAGE_DOCUMENT_PERMISSION
from pyams_zmi.form import AdminEditForm
from pyams_zmi.interfaces import IAdminLayer, IObjectLabel, TITLE_SPAN_BREAK
from pyams_zmi.interfaces.form import IFormTitle
from pyams_zmi.interfaces.table import ITableElementEditor
from pyams_zmi.interfaces.viewlet import IControlPanelMenu, IMenuHeader, IPropertiesMenu, \
    ISiteManagementMenu
from pyams_zmi.table import TableElementEditor
from pyams_zmi.utils import get_object_label
from pyams_zmi.zmi.viewlet.breadcrumb import AdminLayerBreadcrumbItem
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem

__docformat__ = 'restructuredtext'

from pyams_zfiles import _  # pylint: disable=ungrouped-imports


@adapter_config(required=IDocumentContainer,
                provides=IObjectLabel)
def document_container_label(context):
    """Document container label getter"""
    return context.__name__


@viewlet_config(name='document-container.menu',
                context=ISiteRoot, layer=IAdminLayer,
                manager=IControlPanelMenu, weight=40,
                permission=VIEW_SYSTEM_PERMISSION)
class DocumentContainerMenu(NavigationMenuItem):
    """Document container menu"""

    icon_class = 'far fa-file-archive'

    def __new__(cls, context, request, view, manager):  # pylint: disable=unused-argument
        container = query_utility(IDocumentContainer)
        if (container is None) or not container.show_home_menu:
            return None
        return NavigationMenuItem.__new__(cls)

    def __init__(self, context, request, view, manager):
        super().__init__(context, request, view, manager)
        self.container = get_utility(IDocumentContainer)

    @property
    def label(self):
        """Label getter"""
        return self.container.__name__

    def get_href(self):
        """Menu URL getter"""
        return absolute_url(self.container, self.request, 'admin')


@adapter_config(required=(IDocumentContainer, IAdminLayer, Interface, ISiteManagementMenu),
                provides=IMenuHeader)
def document_container_menu_header(context, request, view, manager):  # pylint: disable=unused-argument
    """Document container menu header"""
    return _("Documents container")


@adapter_config(required=(IDocumentContainer, IAdminLayer, Interface),
                provides=ITableElementEditor)
class DocumentContainerElementEditor(TableElementEditor):
    """Document container element editor"""

    view_name = 'admin'
    modal_target = False

    def __new__(cls, context, request, view):  # pylint: disable=unused-argument
        if not request.has_permission(MANAGE_APPLICATION_PERMISSION, context=context) and \
                not request.has_permission(MANAGE_DOCUMENT_PERMISSION, context=context):
            return None
        return TableElementEditor.__new__(cls)


@adapter_config(required=(IDocumentContainer, IAdminLayer, Interface),
                provides=IBreadcrumbItem)
class DocumentContainerBreadcrumbItem(AdminLayerBreadcrumbItem):
    """Document container breadcrumb item"""

    label = _("Documents container")


@viewletmanager_config(name='configuration.menu',
                       context=IDocumentContainer, layer=IAdminLayer,
                       manager=ISiteManagementMenu, weight=20,
                       permission=MANAGE_APPLICATION_PERMISSION,
                       provides=IPropertiesMenu)
class DocumentContainerPropertiesMenu(NavigationMenuItem):
    """Document container properties menu"""

    label = _("Configuration")
    icon_class = 'fas fa-sliders-h'
    href = '#configuration.html'


@ajax_form_config(name='configuration.html',
                  context=IDocumentContainer, layer=IPyAMSLayer,
                  permission=MANAGE_APPLICATION_PERMISSION)
class DocumentContainerConfigurationEditForm(AdminEditForm):
    """Document container properties edit form"""

    title = _("Documents container configuration")
    legend = _("Base configuration")

    fields = Fields(IDocumentContainer).omit('__parent__', '__name__')
