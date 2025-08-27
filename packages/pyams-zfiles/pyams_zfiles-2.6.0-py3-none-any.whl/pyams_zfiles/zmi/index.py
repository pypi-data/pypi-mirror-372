# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from hypatia.interfaces import ICatalog
from pyramid.events import subscriber
from pyramid.view import view_config
from zope.interface import Invalid, implementer

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces.form import IAJAXFormRenderer, IDataExtractedEvent
from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_skin.interfaces.viewlet import IHelpViewletManager
from pyams_skin.viewlet.actions import ContextAddAction
from pyams_skin.viewlet.help import AlertMessage
from pyams_table.column import GetAttrColumn
from pyams_table.interfaces import IColumn, IValues
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.factory import factory_config
from pyams_utils.interfaces.data import IObjectData
from pyams_utils.registry import get_utility
from pyams_utils.url import absolute_url
from pyams_viewlet.viewlet import viewlet_config
from pyams_zfiles.interfaces import ICatalogPropertiesIndexesContainer, ICatalogPropertiesIndexesContainerTarget, \
    ICatalogPropertyIndex, IDocumentContainer, MANAGE_APPLICATION_PERMISSION
from pyams_zfiles.zmi.interfaces import ICatalogPropertiesIndexesTable
from pyams_zmi.form import AdminModalAddForm
from pyams_zmi.helper.container import delete_container_element
from pyams_zmi.helper.event import get_json_table_row_add_callback
from pyams_zmi.interfaces import IAdminLayer, IObjectLabel
from pyams_zmi.interfaces.viewlet import IPropertiesMenu, IToolbarViewletManager
from pyams_zmi.table import NameColumn, Table, TableAdminView, TrashColumn
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem

__docformat__ = 'restructuredtext'

from pyams_zfiles import _


#
# Catalog properties indexes view
#

@viewlet_config(name='catalog-indexes.menu',
                context=ICatalogPropertiesIndexesContainerTarget, layer=IAdminLayer,
                manager=IPropertiesMenu, weight=10,
                permission=MANAGE_APPLICATION_PERMISSION)
class CatalogPropertiesIndexesMenu(NavigationMenuItem):
    """Catalog properties indexes menu"""

    label = _("Catalog indexes")
    href = '#catalog-indexes.html'


@pagelet_config(name='catalog-indexes.html',
                context=ICatalogPropertiesIndexesContainerTarget, layer=IPyAMSLayer,
                permission=MANAGE_APPLICATION_PERMISSION)
class CatalogPropertiesIndexesView(TableAdminView):
    """Catalog properties indexes view"""
    
    title = _("Catalog properties indexes")
    table_class = ICatalogPropertiesIndexesTable
    table_label = _("List of catalog properties indexes")
    
    @property
    def back_url(self):
        """Form back URL getter"""
        return absolute_url(self.context, self.request, 'admin#configuration.html')
    
    back_url_target = None


@viewlet_config(name='catalog-indexes.info',
                context=ICatalogPropertiesIndexesContainerTarget, layer=IAdminLayer,
                view=CatalogPropertiesIndexesView,
                manager=IHelpViewletManager, weight=10)
class CatalogPropertiesIndexesViewInfoMessage(AlertMessage):
    """Catalog properties indexes view information message"""

    _message = _("By default, ZFiles is using a single index to reference properties of "
                 "all documents, which can lead to increase conflict errors if you have many "
                 "documents which share common properties.<br />\n"
                 "Instead, you can choose to create dedicated catalog indexes for a set of selected "
                 "properties.")
    message_renderer = 'markdown'

    status = 'info'
    css_class = 'mt-3 mx-3 mb-1'


@viewlet_config(name='catalog-indexes.warning',
                context=ICatalogPropertiesIndexesContainerTarget, layer=IAdminLayer,
                view=CatalogPropertiesIndexesView,
                manager=IHelpViewletManager, weight=20)
class CatalogPropertiesIndexesViewHelp(AlertMessage):
    """Catalog properties indexes view warning message"""
    
    _message = _("**WARNING**: adding or removing property indexes require rebuild of one or two "
                 "catalog indexes, which can be quite long if you have many documents!")
    message_renderer = 'markdown'
    
    status = 'danger'
    css_class = 'mt-1 mx-3'
    

@factory_config(ICatalogPropertiesIndexesTable)
class CatalogPropertiesIndexesTable(Table):
    """Catalog properties indexes table"""
    
    display_if_empty = True


@adapter_config(required=(ICatalogPropertiesIndexesContainerTarget, IAdminLayer, ICatalogPropertiesIndexesTable),
                provides=IValues)
class CatalogPropertiesIndexesValues(ContextRequestViewAdapter):
    """Catalog properties indexes table values"""
    
    @property
    def values(self):
        """Maps manager layers table values getter"""
        yield from ICatalogPropertiesIndexesContainer(self.context).values()


@adapter_config(name='name',
                required=(ICatalogPropertiesIndexesContainerTarget, IAdminLayer, ICatalogPropertiesIndexesTable),
                provides=IColumn)
class CatalogPropertiesIndexesNameColumn(NameColumn):
    """Catalog properties indexes name column"""

    css_classes = {
        'th': 'w-100'
    }
    

@adapter_config(name='size',
                required=(ICatalogPropertiesIndexesContainerTarget, IAdminLayer, ICatalogPropertiesIndexesTable),
                provides=IColumn)
class CatalogPropertiesIndexesSizeColumn(GetAttrColumn):
    """Catalog properties indexes size column"""
    
    header = _("Documents count")
    
    css_classes = {
        'th': 'pl-2 pr-4',
        'td': 'text-right pr-4'
    }
    weight = 20
    
    def get_value(self, item):
        """Column value getter"""
        catalog = get_utility(ICatalog)
        index_name = f'zfile_property::{item.property_name}'
        return catalog[index_name]._num_docs()


@adapter_config(name='values',
                required=(ICatalogPropertiesIndexesContainerTarget, IAdminLayer, ICatalogPropertiesIndexesTable),
                provides=IColumn)
class CatalogPropertiesIndexesValuesColumn(GetAttrColumn):
    """Catalog properties indexes values column"""
    
    header = _("Distinct values")
    
    css_classes = {
        'th': 'pl-2 pr-4',
        'td': 'text-right pr-4'
    }
    weight = 30
    
    def get_value(self, item):
        """Column value getter"""
        catalog = get_utility(ICatalog)
        index_name = f'zfile_property::{item.property_name}'
        return catalog[index_name].word_count()


@adapter_config(name='trash',
                required=(ICatalogPropertiesIndexesContainerTarget, IAdminLayer, ICatalogPropertiesIndexesTable),
                provides=IColumn)
class CatalogPropertiesIndexesTrashColumn(TrashColumn):
    """Catalog properties indexes trash column"""
    
    permission = MANAGE_APPLICATION_PERMISSION


@view_config(name='delete-element.json',
             context=ICatalogPropertiesIndexesContainerTarget, request_type=IPyAMSLayer,
             permission=MANAGE_APPLICATION_PERMISSION, renderer='json', xhr=True)
def delete_catalog_index(request):
    """Delete catalog index"""
    return delete_container_element(request, ICatalogPropertiesIndexesContainer)


#
# Catalog index add form
#

@viewlet_config(name='add-catalog-index.action',
                context=ICatalogPropertiesIndexesContainerTarget, layer=IAdminLayer, view=ICatalogPropertiesIndexesTable,
                manager=IToolbarViewletManager, weight=10,
                permission=MANAGE_APPLICATION_PERMISSION)
class CatalogPropertyIndexAddAction(ContextAddAction):
    """Catalog property index add action"""

    label = _("Add new catalog property index")
    href = 'add-catalog-index.html'


@ajax_form_config(name='add-catalog-index.html',
                  context=ICatalogPropertiesIndexesContainerTarget, layer=IPyAMSLayer,
                  permission=MANAGE_APPLICATION_PERMISSION)
@implementer(IObjectData)
class CatalogPropertyIndexAddForm(AdminModalAddForm):
    """Catalog property index add form"""

    @property
    def subtitle(self):
        translate = self.request.localizer.translate
        return translate(_("New property index"))

    legend = _("New index properties")
    fields = Fields(ICatalogPropertyIndex)
    content_factory = ICatalogPropertyIndex

    object_data = {
        'ams-form-progress-handler': 'get-progress-status.json',
        'ams-form-progress-field-name': 'progress_id',
        'ams-form-progress-interval': 5000
    }

    def add(self, obj):
        ICatalogPropertiesIndexesContainer(self.context).append(obj)


@subscriber(IDataExtractedEvent, form_selector=CatalogPropertyIndexAddForm)
def handle_new_catalog_index_data(event):
    """Handle new index data extraction"""
    container = IDocumentContainer(event.form.context)
    name = event.data.get('name')
    if name in ICatalogPropertiesIndexesContainer(container).index_names:
        event.form.widgets.errors += (Invalid(_("Catalog index with specified property name already exists!")))


@adapter_config(required=(ICatalogPropertiesIndexesContainerTarget, IAdminLayer, CatalogPropertyIndexAddForm),
                provides=IAJAXFormRenderer)
class CatalogPropertyIndexAddFormRenderer(ContextRequestViewAdapter):
    """Catalog property add form AJAX renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if changes is None:  # WARNING: creating an empty container will return a "false" value!
            return None
        container = get_utility(IDocumentContainer)
        return {
            'callbacks': [
                get_json_table_row_add_callback(container, self.request,
                                                ICatalogPropertiesIndexesTable, changes)
            ]
        }


@adapter_config(required=(ICatalogPropertyIndex, IPyAMSLayer),
                provides=IObjectLabel)
def catalog_property_index_label(context, request):
    """Catalog property label adapter"""
    return context.property_name
