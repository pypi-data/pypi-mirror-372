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

"""PyAMS_zfiles.zmi.synchronizer module

This module defines management views for synchronization utility.
"""

from pyramid.decorator import reify
from pyramid.view import view_config
from pyramid.events import subscriber
from zope.interface import Interface, Invalid

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces import DISPLAY_MODE
from pyams_form.interfaces.form import IAJAXFormRenderer, IDataExtractedEvent
from pyams_layer.interfaces import IPyAMSLayer
from pyams_skin.interfaces.view import IModalEditForm
from pyams_skin.interfaces.viewlet import IFormFooterViewletManager
from pyams_skin.viewlet.actions import ContextAddAction
from pyams_table.column import GetAttrColumn
from pyams_table.interfaces import IColumn, IValues
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.traversing import get_parent
from pyams_utils.url import absolute_url
from pyams_viewlet.viewlet import viewlet_config
from pyams_zfiles.interfaces import IDocumentContainer, IDocumentSynchronizer, \
    IDocumentSynchronizerConfiguration, MANAGE_APPLICATION_PERMISSION
from pyams_zfiles.zmi import DocumentContainerConfigurationEditForm
from pyams_zmi.form import AdminModalAddForm, AdminModalEditForm
from pyams_zmi.helper.container import delete_container_element, switch_element_attribute
from pyams_zmi.helper.event import get_json_table_row_refresh_callback
from pyams_zmi.interfaces import IAdminLayer, IObjectLabel, TITLE_SPAN_BREAK
from pyams_zmi.interfaces.form import IFormTitle
from pyams_zmi.interfaces.table import ITableElementEditor
from pyams_zmi.interfaces.viewlet import IToolbarViewletManager
from pyams_zmi.table import ActionColumn, AttributeSwitcherColumn, I18nColumnMixin, \
    IconColumn, InnerTableAdminView, Table, TableElementEditor, TrashColumn

__docformat__ = 'restructuredtext'

from pyams_zfiles import _  # pylint: disable=ungrouped-imports
from pyams_zmi.utils import get_object_label


class DocumentSynchronizerConfigurationTable(Table):
    """Document synchronizer configurations table"""

    display_if_empty = True

    @reify
    def data_attributes(self):
        attributes = super().data_attributes
        synchronizer = IDocumentSynchronizer(self.context)
        attributes['table'].update({
            'data-ams-location': absolute_url(synchronizer, self.request),
            'data-ams-order': '2,asc'
        })
        return attributes


@adapter_config(required=(IDocumentSynchronizer, IAdminLayer,
                          DocumentSynchronizerConfigurationTable),
                provides=IValues)
class DocumentSynchronizerConfigurationTableValues(ContextRequestViewAdapter):
    """Document synchronizer configurations table values"""

    @property
    def values(self):
        """Values getter"""
        yield from IDocumentSynchronizer(self.context).values()


@adapter_config(name='enabled',
                required=(IDocumentSynchronizer, IAdminLayer,
                          DocumentSynchronizerConfigurationTable),
                provides=IColumn)
class DocumentSynchronizerConfigurationEnabledColumn(AttributeSwitcherColumn):
    """Synchronizer configuration switcher column"""

    hint = _("Click icon to enable or disable configuration")

    attribute_name = 'enabled'
    attribute_switcher = 'switch-enabled-configuration.json'

    icon_on_class = 'fas fa-user'
    icon_off_class = 'fas fa-user-slash text-danger'


@view_config(name='switch-enabled-configuration.json',
             context=IDocumentSynchronizer, request_type=IPyAMSLayer,
             renderer='json', xhr=True)
def switch_enabled_configuration(request):
    """Switch enabled configuration"""
    return switch_element_attribute(request, container_factory=IDocumentSynchronizer)


@adapter_config(name='roles',
                required=(IDocumentSynchronizer, IAdminLayer,
                          DocumentSynchronizerConfigurationTable),
                provides=IColumn)
class DocumentSynchronizerConfigurationRolesColumn(ActionColumn):
    """Document synchronizer configuration roles column"""

    href = 'modal-object-roles.html'
    permission = MANAGE_APPLICATION_PERMISSION

    icon_class = 'fas fa-shield-alt'
    hint = _("Users roles")

    weight = 10


@adapter_config(name='name',
                required=(IDocumentSynchronizer, IAdminLayer,
                          DocumentSynchronizerConfigurationTable),
                provides=IColumn)
class DocumentSynchronizerConfigurationNameColumn(I18nColumnMixin, GetAttrColumn):
    """Synchronizer configurations name column"""

    attr_name = 'name'
    i18n_header = _("Name")

    weight = 20


@adapter_config(name='target',
                required=(IDocumentSynchronizer, IAdminLayer,
                          DocumentSynchronizerConfigurationTable),
                provides=IColumn)
class DocumentSynchronizerConfigurationTargetColumn(I18nColumnMixin, GetAttrColumn):
    """Synchronizer configurations target column"""

    attr_name = 'target'
    i18n_header = _("Target")

    weight = 30


@adapter_config(name='mode',
                required=(IDocumentSynchronizer, IAdminLayer,
                          DocumentSynchronizerConfigurationTable),
                provides=IColumn)
class DocumentSynchronizerConfigurationModeColumn(IconColumn):
    """Synchronizer configurations mode column"""
    
    export_icon_class = 'fas fa-file-export'
    export_hint = _("Export mode")
    
    import_icon_class = 'fas fa-file-import'
    import_hint = _("Import mode")
    
    weight = 40
    
    def get_icon_class(self, item):
        return self.import_icon_class if item.mode == 'import' else self.export_icon_class
    
    def get_icon_hint(self, item):
        translate = self.request.localizer.translate
        return translate(self.import_hint if item.mode == 'import' else self.export_hint)
    
    
@adapter_config(name='trash',
                required=(IDocumentSynchronizer, IAdminLayer,
                          DocumentSynchronizerConfigurationTable),
                provides=IColumn)
class DocumentSynchronizerConfigurationTrashColumn(TrashColumn):
    """Synchronizer configurations table trash column"""


@view_config(name='delete-element.json',
             context=IDocumentSynchronizer, request_type=IPyAMSLayer,
             renderer='json', xhr=True)
def delete_configuration(request):
    """Delete configuration"""
    return delete_container_element(request, container_factory=IDocumentSynchronizer)


@viewlet_config(name='synchronizer-configurations-table',
                context=IDocumentContainer, layer=IAdminLayer,
                view=DocumentContainerConfigurationEditForm,
                manager=IFormFooterViewletManager, weight=10)
class DocumentSynchronizerConfigurationsTableView(InnerTableAdminView):
    """Documents synchronizer configurations table view"""

    table_class = DocumentSynchronizerConfigurationTable
    table_label = _("Synchronizer configurations")

    container_intf = IDocumentSynchronizer


#
# Configuration add form
#

@viewlet_config(name='add-configuration.menu',
                context=IDocumentContainer, layer=IAdminLayer,
                view=DocumentSynchronizerConfigurationTable,
                manager=IToolbarViewletManager, weight=10,
                permission=MANAGE_APPLICATION_PERMISSION)
class ConfigurationAddAction(ContextAddAction):
    """Documents synchronizer configuration add action"""

    label = _("Add configuration")
    href = 'add-configuration.html'


@ajax_form_config(name='add-configuration.html',
                  context=IDocumentContainer, layer=IPyAMSLayer,
                  permission=MANAGE_APPLICATION_PERMISSION)
class ConfigurationAddForm(AdminModalAddForm):
    """Documents synchronizer configuration add form"""

    subtitle = _("New configuration")
    legend = _("New configuration properties")

    fields = Fields(IDocumentSynchronizerConfiguration).omit('enabled')
    content_factory = IDocumentSynchronizerConfiguration

    def add(self, obj):
        synchronizer = IDocumentSynchronizer(self.context)
        synchronizer[obj.name] = obj


@adapter_config(required=(IDocumentContainer, IAdminLayer, ConfigurationAddForm),
                provides=IFormTitle)
def document_container_form_title(context, request, form):
    """Document container synchronizer configuration add form title"""
    translate = request.localizer.translate
    return TITLE_SPAN_BREAK.format(
        get_object_label(context, request, form),
        translate(_("Documents synchronizer")))


@subscriber(IDataExtractedEvent, form_selector=ConfigurationAddForm)
def handle_configuration_add_form_data(event):
    """Handle configuration add form data extraction"""
    name = event.data.get('name')
    context = IDocumentSynchronizer(event.form.context)
    if name in context:
        event.form.widgets.errors += (Invalid(_("Provided name is already used!")),)


@adapter_config(required=(IDocumentSynchronizerConfiguration, IAdminLayer, Interface),
                provides=ITableElementEditor)
class DocumentSynchronizerConfigurationEditor(TableElementEditor):
    """Document synchronizer configuration editor"""


@ajax_form_config(name='properties.html',
                  context=IDocumentSynchronizerConfiguration, layer=IPyAMSLayer,
                  permission=MANAGE_APPLICATION_PERMISSION)
class ConfigurationEditForm(AdminModalEditForm):
    """Documents synchronizer configuration edit form"""

    @property
    def subtitle(self):
        translate = self.request.localizer.translate
        return translate(_("Configuration: {}")).format(self.context.name)

    legend = _("Configuration properties")

    fields = Fields(IDocumentSynchronizerConfiguration).omit('enabled')

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        name = self.widgets.get('name')
        if name is not None:
            name.mode = DISPLAY_MODE


@adapter_config(required=(IDocumentSynchronizerConfiguration, IAdminLayer, IModalEditForm),
                provides=IFormTitle)
def document_synchronizer_edit_form_title(context, request, form):
    """Document synchronizer configuration edit form title"""
    container = get_parent(context, IDocumentContainer)
    return document_container_form_title(container, request, form)


@adapter_config(name='apply',
                required=(IDocumentSynchronizerConfiguration, IAdminLayer, ConfigurationEditForm),
                provides=IAJAXFormRenderer)
class ConfigurationEditFormRenderer(ContextRequestViewAdapter):
    """Configuration edit form renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if not changes:
            return None
        manager = get_parent(self.context, IDocumentSynchronizer)
        return {
            'callbacks': [
                get_json_table_row_refresh_callback(manager, self.request,
                                                    DocumentSynchronizerConfigurationTable,
                                                    self.context)
            ]
        }


@adapter_config(required=(IDocumentSynchronizerConfiguration, IAdminLayer, Interface),
                provides=IObjectLabel)
def document_synchronizer_configuration_label(context, request, view):  # pylint: disable=unused-argument
    """Document synchronizer configuration label adapter"""
    translate = request.localizer.translate
    return translate(_("Synchronizer configuration: {} ")).format(context.name)
