# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from pyramid.decorator import reify
from pyramid.events import subscriber
from pyramid.view import view_config
from zope.interface import Interface, Invalid
from zope.schema import Dict, TextLine

from pyams_file.interfaces import IFile
from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.group import Group
from pyams_form.interfaces import DISPLAY_MODE
from pyams_form.interfaces.form import IAJAXFormRenderer, IDataExtractedEvent, IGroup
from pyams_form.interfaces.widget import IWidget
from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_skin.interfaces.view import IModalEditForm
from pyams_skin.interfaces.viewlet import IContextActionsViewletManager, IHelpViewletManager
from pyams_skin.viewlet.actions import ContextAction, ContextAddAction
from pyams_skin.viewlet.help import AlertMessage
from pyams_skin.widget.dict import DictFieldWidget
from pyams_table.column import GetAttrColumn
from pyams_table.interfaces import IColumn, IValues
from pyams_utils.adapter import ContextAdapter, ContextRequestViewAdapter, adapter_config
from pyams_utils.factory import factory_config
from pyams_utils.registry import get_utility
from pyams_utils.traversing import get_parent
from pyams_utils.url import absolute_url
from pyams_viewlet.viewlet import EmptyViewlet, viewlet_config
from pyams_zfiles.interfaces import IDocumentContainer, IDocumentPropertyExtractorContainer, \
    IDocumentPropertyExtractorContainerTarget, IDocumentPropertyExtractorInfo, IDocumentVersion, \
    MANAGE_APPLICATION_PERMISSION, \
    READ_DOCUMENT_PERMISSION
from pyams_zfiles.zmi.interfaces import IDocumentPropertiesExtractorsTable
from pyams_zmi.form import AdminModalAddForm, AdminModalDisplayForm, AdminModalEditForm
from pyams_zmi.helper.container import delete_container_element, switch_element_attribute
from pyams_zmi.helper.event import get_json_table_row_add_callback, get_json_table_row_refresh_callback
from pyams_zmi.interfaces import IAdminLayer, IObjectLabel, TITLE_SPAN_BREAK
from pyams_zmi.interfaces.form import IFormTitle
from pyams_zmi.interfaces.table import ITableElementEditor
from pyams_zmi.interfaces.viewlet import IPropertiesMenu, IToolbarViewletManager
from pyams_zmi.table import AttributeSwitcherColumn, I18nColumnMixin, IconColumn, NameColumn, Table, TableAdminView, \
    TableElementEditor, TrashColumn
from pyams_zmi.utils import get_object_label
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem

__docformat__ = 'restructuredtext'

from pyams_zfiles import _


#
# Document properties extractors view
#

@viewlet_config(name='properties-extractors.menu',
                context=IDocumentPropertyExtractorContainerTarget, layer=IAdminLayer,
                manager=IPropertiesMenu, weight=20,
                permission=MANAGE_APPLICATION_PERMISSION)
class DocumentPropertiesExtractorsMenu(NavigationMenuItem):
    """Document properties extractors menu"""

    label = _("Properties extractors")
    href = '#properties-extractors.html'
    
    
@pagelet_config(name='properties-extractors.html',
                context=IDocumentPropertyExtractorContainerTarget, layer=IPyAMSLayer,
                permission=MANAGE_APPLICATION_PERMISSION)
class DocumentPropertiesExtractorsView(TableAdminView):
    """Document properties extractors view"""
    
    title = _("Document properties extractors")
    table_class = IDocumentPropertiesExtractorsTable
    table_label = _("List of documents properties extractors")
    
    container_intf = IDocumentPropertyExtractorContainer
    
    @property
    def back_url(self):
        """Form back URL"""
        return absolute_url(self.context. self.request, 'admin#configuration.html')
    
    back_url_target = None


@viewlet_config(name='properties-extractors.info',
                context=IDocumentPropertyExtractorContainerTarget, layer=IAdminLayer,
                view=DocumentPropertiesExtractorsView,
                manager=IHelpViewletManager, weight=10)
class DocumentPropertiesExtractorsViewInfoMessage(AlertMessage):
    """Document properties extractors view information message"""

    _message = _("You can use properties extractors to extract properties from a document content.<br />"
                 "This option requires a \"content extractor\", to convert document content into a text "
                 "representation on which regular expressions will be used to extract new properties; "
                 "extractors actually exist for text and PDF files.")
    message_renderer = 'markdown'

    status = 'info'
    css_class = 'mt-3 mx-3'


@factory_config(IDocumentPropertiesExtractorsTable)
class DocumentPropertiesExtractorsTable(Table):
    """Document properties extractors table"""
    
    display_if_empty = True

    @reify
    def data_attributes(self):
        attributes = super().data_attributes
        container = IDocumentPropertyExtractorContainer(self.context)
        attributes['table'].update({
            'data-ams-location': absolute_url(container, self.request),
            'data-ams-order': '1,asc'
        })
        return attributes


@adapter_config(required=(IDocumentPropertyExtractorContainer, IAdminLayer, IDocumentPropertiesExtractorsTable),
                provides=IValues)
class DocumentPropertiesExtractorsValues(ContextRequestViewAdapter):
    """Document properties extractors table values"""
    
    @property
    def values(self):
        """Maps manager layers table values getter"""
        yield from IDocumentPropertyExtractorContainer(self.context).values()


@adapter_config(name='active',
                required=(IDocumentPropertyExtractorContainer, IAdminLayer, IDocumentPropertiesExtractorsTable),
                provides=IColumn)
class DocumentPropertiesExtractorsActiveColumn(AttributeSwitcherColumn):
    """Document properties extractors active column"""
    
    hint = _("CLick icon to enable or disable property extractor")
    
    attribute_name = 'active'
    attribute_switcher = 'switch-active-extractor.json'
    
    icon_on_class = 'far fa-check-square'
    icon_off_class = 'far fa-square text-danger'
    
    weight = 10


@view_config(name='switch-active-extractor.json',
             context=IDocumentPropertyExtractorContainer, request_type=IPyAMSLayer,
             renderer='json', xhr=True)
def switch_active_extractor(request):
    """Switch active document properties extractor"""
    return switch_element_attribute(request, container_factory=IDocumentPropertyExtractorContainer)


@adapter_config(name='name',
                required=(IDocumentPropertyExtractorContainer, IAdminLayer, IDocumentPropertiesExtractorsTable),
                provides=IColumn)
class DocumentPropertiesExtractorsNameColumn(NameColumn):
    """Document properties extractors name column"""
    
    attr_name = 'name'


@adapter_config(name='property_name',
                required=(IDocumentPropertyExtractorContainer, IAdminLayer, IDocumentPropertiesExtractorsTable),
                provides=IColumn)
class DocumentPropertiesExtractorsPropertyNameColumn(I18nColumnMixin, GetAttrColumn):
    """Document properties extractors property name column"""

    i18n_header = _("Property name")
    attr_name = 'property_name'

    weight = 20


@adapter_config(name='override',
                required=(IDocumentPropertyExtractorContainer, IAdminLayer, IDocumentPropertiesExtractorsTable),
                provides=IColumn)
class DocumentPropertiesExtractorsOverrideColumn(IconColumn):
    """Document properties extractors override column"""

    icon_class = 'fas fa-plus-circle'
    hint = _("This extractor can override an existing property")

    weight = 30

    def get_icon(self, item):
        if not item.override:
            return ''
        return super().get_icon(item)


@adapter_config(name='multilines',
                required=(IDocumentPropertyExtractorContainer, IAdminLayer, IDocumentPropertiesExtractorsTable),
                provides=IColumn)
class DocumentPropertiesExtractorsMultilinesColumn(IconColumn):
    """Document properties extractors multilines column"""

    icon_class = 'fas fa-grip-lines'
    hint = _("This extractor is multi-lines")

    weight = 32

    def get_icon(self, item):
        if not item.multiline:
            return ''
        return super().get_icon(item)


@adapter_config(name='searchall',
                required=(IDocumentPropertyExtractorContainer, IAdminLayer, IDocumentPropertiesExtractorsTable),
                provides=IColumn)
class DocumentPropertiesExtractorsSearchallColumn(IconColumn):
    """Document properties extractors search-all column"""

    icon_class = 'fas fa-tasks'
    hint = _("This extractor can extract several values")

    weight = 34

    def get_icon(self, item):
        if not item.search_all_occurrences:
            return ''
        return super().get_icon(item)


@adapter_config(name='filtered',
                required=(IDocumentPropertyExtractorContainer, IAdminLayer, IDocumentPropertiesExtractorsTable),
                provides=IColumn)
class DocumentPropertiesExtractorsPropertyNameFilteredColumn(IconColumn):
    """Document properties extractors filtered column"""

    icon_class = 'fas fa-filter'
    hint = _("This extractor is used only for documents matching selected applications of properties")
    
    weight = 36
    
    def get_icon(self, item):
        if not (item.application_names or item.properties):
            return ''
        return super().get_icon(item)
    
    
@adapter_config(name='trash',
                required=(IDocumentPropertyExtractorContainer, IAdminLayer, IDocumentPropertiesExtractorsTable),
                provides=IColumn)
class DocumentPropertiesExtractorsTrashColumn(TrashColumn):
    """Document properties extractors trash column"""
    
    permission = MANAGE_APPLICATION_PERMISSION


@view_config(name='delete-element.json',
             context=IDocumentPropertyExtractorContainer, request_type=IPyAMSLayer,
             permission=MANAGE_APPLICATION_PERMISSION, renderer='json', xhr=True)
def delete_property_extractor(request):
    """Delete property extractor"""
    return delete_container_element(request, IDocumentPropertyExtractorContainer)


#
# Document property extractor add form
#


@viewlet_config(name='add-property-extractor.action',
                context=IDocumentPropertyExtractorContainerTarget, layer=IAdminLayer,
                view=IDocumentPropertiesExtractorsTable,
                manager=IToolbarViewletManager, weight=10,
                permission=MANAGE_APPLICATION_PERMISSION)
class DocumentPropertyExtractorAddAction(ContextAddAction):
    """Document property extractor add action"""
    
    label = _("Add new document property extractor")
    href = 'add-property-extractor.html'
    
    def get_href(self):
        container = IDocumentPropertyExtractorContainer(self.context)
        return absolute_url(container, self.request, self.href)
    
    
@ajax_form_config(name='add-property-extractor.html',
                  context=IDocumentPropertyExtractorContainer, layer=IPyAMSLayer,
                  permission=MANAGE_APPLICATION_PERMISSION)
class DocumentPropertyExtractorAddForm(AdminModalAddForm):
    """Document property extractor add form"""
    
    @property
    def subtitle(self):
        translate = self.request.localizer.translate
        return translate(_("New property extractor"))
    
    legend = _("New exctractor properties")

    fields = Fields(IDocumentPropertyExtractorInfo).omit('active')
    fields['properties'].widget_factory = DictFieldWidget

    content_factory = IDocumentPropertyExtractorInfo

    def add(self, obj):
        IDocumentPropertyExtractorContainer(self.context).append(obj)


@subscriber(IDataExtractedEvent, form_selector=DocumentPropertyExtractorAddForm)
def handle_new_property_extractor_data(event):
    """Handle new property extractor data extraction"""
    name = event.data.get('name')
    if name in IDocumentPropertyExtractorContainer(event.form.context):
        event.form.widgets.errors += (Invalid(_("Property extractor with specified name already exists!")))


@adapter_config(required=(IDocumentPropertyExtractorContainer, IAdminLayer,
                          DocumentPropertyExtractorAddForm),
                provides=IAJAXFormRenderer)
class DocumentPropertyExtractorAddFormRenderer(ContextRequestViewAdapter):
    """Document property extractor add form AJAX renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if changes is None:  # WARNING: creating an empty container will return a "false" value!
            return None
        return {
            'callbacks': [
                get_json_table_row_add_callback(self.context, self.request,
                                                IDocumentPropertiesExtractorsTable, changes)
            ]
        }


@adapter_config(required=(IDocumentPropertyExtractorInfo, IAdminLayer, Interface),
                provides=ITableElementEditor)
class DocumentPropertyExtractorEditor(TableElementEditor):
    """Document property extractor editor"""
    
    
@ajax_form_config(name='properties.html',
                  context=IDocumentPropertyExtractorInfo, layer=IPyAMSLayer,
                  permission=MANAGE_APPLICATION_PERMISSION)
class DocumentPropertyExtractorEditForm(AdminModalEditForm):
    """Document property extractor edit form"""

    @property
    def subtitle(self):
        translate = self.request.localizer.translate
        return translate(_("Property extractor: {}")).format(self.context.name)

    legend = _("Property extractor properties")
    
    fields = Fields(IDocumentPropertyExtractorInfo).omit('active')
    fields['properties'].widget_factory = DictFieldWidget
    
    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        name = self.widgets.get('name')
        if name is not None:
            name.mode = DISPLAY_MODE


@adapter_config(name='apply',
                required=(IDocumentPropertyExtractorInfo, IAdminLayer, IModalEditForm),
                provides=IAJAXFormRenderer)
class DocumentPropertyExtractorEditFormRenderer(ContextRequestViewAdapter):
    """Document property extractor edit form renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if not changes:
            return None
        container = get_parent(self.context, IDocumentPropertyExtractorContainer)
        return {
            'callbacks': [
                get_json_table_row_refresh_callback(container, self.request,
                                                    IDocumentPropertiesExtractorsTable,
                                                    self.context)
            ]
        }


@adapter_config(required=(IDocumentPropertyExtractorContainer, IAdminLayer, DocumentPropertyExtractorAddForm),
                provides=IFormTitle)
@adapter_config(required=(IDocumentPropertyExtractorInfo, IAdminLayer, DocumentPropertyExtractorEditForm),
                provides=IFormTitle)
def document_property_extractor_edit_form_title(context, request, form):
    """Document property extractor edit form title"""
    container = get_parent(context, IDocumentContainer)
    translate = request.localizer.translate
    return TITLE_SPAN_BREAK.format(
        get_object_label(container, request, form),
        translate(_("Documents properties extractors")))


@adapter_config(required=(IDocumentPropertyExtractorInfo, IPyAMSLayer),
                provides=IObjectLabel)
def document_property_extractor_label(context, request):
    """Document property extractor label getter"""
    return context.name


#
# File extractors tester
#

@viewlet_config(name='test-extractors.action',
                context=IFile, layer=IAdminLayer, view=IWidget,
                manager=IContextActionsViewletManager, weight=15,
                permission=READ_DOCUMENT_PERMISSION)
class ExtractorsTestAction(ContextAction):
    """Extractors test action"""

    def __new__(cls, context, request, view, manager):
        parent = context.__parent__
        if not IDocumentVersion.providedBy(parent):
            return None
        return ContextAction.__new__(cls)

    hint = _("Test properties extractors")
    icon_class = 'fas fa-file-export'

    href = 'test-extractors.html'
    modal_target = True


@ajax_form_config(name='test-extractors.html',
                  context=IFile, layer=IPyAMSLayer,
                  permission=READ_DOCUMENT_PERMISSION)
class ExtractorsTestForm(AdminModalDisplayForm):
    """Extractors test form"""

    subtitle = _("Document properties extraction test")
    legend = _("Extractors test output")

    fields = Fields(Interface)


class IExtractorsTestOutput(Interface):
    """Extractors test output interface"""

    properties = Dict(title=_("Extracted properties"),
                      description=_("Values of properties extracted for this document"),
                      required=False,
                      key_type=TextLine(),
                      value_type=TextLine())


@adapter_config(required=IFile,
                provides=IExtractorsTestOutput)
class DocumentVersionPropertiesExtractor(ContextAdapter):
    """Document version properties extractor"""

    def __init__(self, context):
        super().__init__(context)
        document = context.__parent__
        container = get_utility(IDocumentContainer)
        extractors = IDocumentPropertyExtractorContainer(container)
        self.properties = extractors.extract_properties(document, force=True)


@adapter_config(name='extractors-output',
                required=(IFile, IAdminLayer, ExtractorsTestForm),
                provides=IGroup)
class ExtractorsTestOutput(Group):
    """Extractors test output"""

    legend = _("Extractors test output")

    fields = Fields(IExtractorsTestOutput)
    fields['properties'].widget_factory = DictFieldWidget

    def update_widgets(self, prefix=None, use_form_mode=True):
        super().update_widgets(prefix, use_form_mode)
        properties = self.widgets.get('properties')
        if properties is not None:
            properties.mode = DISPLAY_MODE
            if not properties.value:
                translate = self.request.localizer.translate
                properties.value = translate(_("No property was extracted for this document!"))
