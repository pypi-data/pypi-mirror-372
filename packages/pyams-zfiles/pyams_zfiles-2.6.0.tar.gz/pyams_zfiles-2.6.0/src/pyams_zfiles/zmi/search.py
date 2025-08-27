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

"""PyAMS_zfiles.zmi.search module

This module provides ZFiles search features.
"""
from pyramid.decorator import reify
from zope.dublincore.interfaces import IZopeDublinCore
from zope.interface import Interface, implementer
from zope.schema import Choice, Int, TextLine

from pyams_form.field import Fields
from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_security.schema import PrincipalField
from pyams_table.column import GetAttrColumn
from pyams_table.interfaces import IColumn, IValues
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.date import SH_DATETIME_FORMAT, format_datetime
from pyams_utils.interfaces.data import IObjectData
from pyams_utils.schema import DatesRangeField
from pyams_viewlet.viewlet import viewlet_config
from pyams_workflow.interfaces import IWorkflowState
from pyams_zfiles.interfaces import IDocumentContainer, PYAMS_ZFILES_APPLICATIONS_VOCABULARY, \
    STATE_LABELS
from pyams_zfiles.workflow import STATES_VOCABULARY
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.viewlet import ISiteManagementMenu
from pyams_zmi.search import SearchForm, SearchResultsView, SearchView
from pyams_zmi.table import DateColumn, I18nColumnMixin, Table
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem


__docformat__ = 'restructuredtext'

from pyams_zfiles import _  # pylint: disable=ungrouped-imports


@viewlet_config(name='search.menu',
                context=IDocumentContainer, layer=IAdminLayer,
                manager=ISiteManagementMenu, weight=10,
                permission=VIEW_SYSTEM_PERMISSION)
class DocumentContainerSearchMenu(NavigationMenuItem):
    """Document container search menu"""

    label = _("Search document")
    icon_class = 'fas fa-search'
    href = '#search.html'


class IDocumentSearchFields(Interface):
    """Document search interface"""

    oid = TextLine(title=_("Document OID"),
                   description=_("Document unique identifier"),
                   required=False)

    version = Int(title=_("Document version"),
                  required=False)

    title = TextLine(title=_("Document title"),
                     description=_("User friendly name of the document"),
                     required=False)

    application_name = Choice(title=_("Source application"),
                              description=_("Name of the application which submitted "
                                            "the document"),
                              vocabulary=PYAMS_ZFILES_APPLICATIONS_VOCABULARY,
                              required=False)

    hash = TextLine(title=_("File hash"),
                    description=_("Document file hash"),
                    required=False)

    properties = TextLine(title=_("Properties"),
                          description=_("Document properties; you can set properties names and "
                                        "values using URL encoding, like in \"property_name="
                                        "value1&another_prop=value2\"; if you set the same "
                                        "property several times, the property values will be "
                                        "combined with an \"or\""),
                          required=False)

    tags = TextLine(title=_("Tag"),
                    description=_("Document tag; you can enter several tags by separating them "
                                  "with semicolons"),
                    required=False)

    status = Choice(title=_("Document status"),
                    description=_("Workflow state of searched documents"),
                    vocabulary=STATES_VOCABULARY,
                    required=False)

    creator = PrincipalField(title=_("Creator"),
                             description=_("Name of the principal which created the document"),
                             required=False)

    created_date = DatesRangeField(title=_("Creation dates"),
                                   description=_("Dates at which the document (or one of it's "
                                                 "versions) was created; first date is included, "
                                                 "second date is excluded"),
                                   required=False)

    owner = PrincipalField(title=_("Owner"),
                           description=_("Name of the principal owning the document"),
                           required=False)

    updater = PrincipalField(title=_("Updater"),
                             description=_("Last document updater principal ID"),
                             required=False)

    updated_date = DatesRangeField(title=_("Modification dates"),
                                   description=_("Dates at which the document (or one of it's "
                                                 "versions) was modified for the last time; "
                                                 "first date is included, second one is "
                                                 "excluded"),
                                   required=False)

    status_updater = PrincipalField(title=_("Status updater"),
                                    description=_("Last workflow status updater principal ID"),
                                    required=False)

    status_update_date = DatesRangeField(title=_("Status update dates"),
                                         description=_("Dates at which the document status (or "
                                                       "one of it's versions) was modified for "
                                                       "the last time; first date is included, "
                                                       "second one is excluded"),
                                         required=False)


@implementer(IObjectData)  # pylint: disable=abstract-method
class DocumentSearchForm(SearchForm):
    """Document search form"""

    title = _("Documents search form")

    fields = Fields(IDocumentSearchFields)
    label_css_class = 'col-sm-3'
    input_css_class = 'col-sm-9'

    object_data = {
        'ams-warn-on-change': False
    }

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        oid = self.widgets.get('oid')
        if oid is not None:
            oid.input_css_class = 'col-sm-3'
        version = self.widgets.get('version')
        if version is not None:
            version.input_css_class = 'col-sm-3'
        placeholder = self.request.localizer.translate(_("No selected principal"))
        creator = self.widgets.get('creator')
        if creator is not None:
            creator.placeholder = placeholder
        owner = self.widgets.get('owner')
        if owner is not None:
            owner.placeholder = placeholder
        updater = self.widgets.get('updater')
        if updater is not None:
            updater.placeholder = placeholder
        status_updater = self.widgets.get('status_updater')
        if status_updater is not None:
            status_updater.placeholder = placeholder


@pagelet_config(name='search.html', context=IDocumentContainer, layer=IPyAMSLayer,
                permission=VIEW_SYSTEM_PERMISSION)
class DocumentSearchView(SearchView):
    """Document search view"""

    title = _("Documents search form")
    search_form = DocumentSearchForm


class DocumentSearchResultsTable(Table):
    """Document search table"""


@adapter_config(required=(IDocumentContainer, IAdminLayer, DocumentSearchResultsTable),
                provides=IValues)
class DocumentSearchResultsValues(ContextRequestViewAdapter):
    """Document search results values"""

    @reify
    def values(self):
        """Document search table results getter"""
        form = DocumentSearchForm(self.context, self.request)
        form.update()
        data, _errors = form.extract_data()
        yield from self.context.find_documents(data)


@adapter_config(name='oid',
                required=(IDocumentContainer, IAdminLayer, DocumentSearchResultsTable),
                provides=IColumn)
class DocumentOidColumn(I18nColumnMixin, GetAttrColumn):
    """Document OID column"""

    i18n_header = _("OID")
    attr_name = 'oid'

    weight = 10


@adapter_config(name='title',
                required=(IDocumentContainer, IAdminLayer, DocumentSearchResultsTable),
                provides=IColumn)
class DocumentTitleColumn(I18nColumnMixin, GetAttrColumn):
    """Document title column"""

    i18n_header = _("Title")
    attr_name = 'title'

    weight = 15


@adapter_config(name='application_name',
                required=(IDocumentContainer, IAdminLayer, DocumentSearchResultsTable),
                provides=IColumn)
class DocumentApplicationNameColumn(I18nColumnMixin, GetAttrColumn):
    """Document application name column"""

    i18n_header = _("Application")
    attr_name = 'application_name'

    weight = 20


@adapter_config(name='state',
                required=(IDocumentContainer, IAdminLayer, DocumentSearchResultsTable),
                provides=IColumn)
class DocumentStatusColumn(I18nColumnMixin, GetAttrColumn):
    """Document state column"""

    i18n_header = _("State")
    attr_name = 'state'

    weight = 30

    def get_value(self, obj):
        state = IWorkflowState(obj)
        return self.request.localizer.translate(STATE_LABELS.get(state.state))


@adapter_config(name='version',
                required=(IDocumentContainer, IAdminLayer, DocumentSearchResultsTable),
                provides=IColumn)
class DocumentVersionColumn(I18nColumnMixin, GetAttrColumn):
    """Document state column"""

    i18n_header = _("Version")
    attr_name = 'version'

    weight = 40

    def get_value(self, obj):
        state = IWorkflowState(obj)
        return state.version_id


@adapter_config(name='creation_time',
                required=(IDocumentContainer, IAdminLayer, DocumentSearchResultsTable),
                provides=IColumn)
class DocumentCreationTimeColumn(I18nColumnMixin, DateColumn):
    """Document creation time column"""

    i18n_header = _("Creation time")
    attr_name = 'created'
    formatter = SH_DATETIME_FORMAT

    weight = 50

    def get_value(self, obj):
        dc = IZopeDublinCore(obj)  # pylint: disable=invalid-name
        return format_datetime(dc.created, self.formatter, self.request)


@pagelet_config(name='search-results.html', context=IDocumentContainer, layer=IPyAMSLayer,
                permission=VIEW_SYSTEM_PERMISSION, xhr=True)
class DocumentSearchResultsView(SearchResultsView):
    """Document search results view"""

    table_label = _("Search results")
    table_class = DocumentSearchResultsTable
