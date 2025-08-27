# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

import transaction
from hypatia.interfaces import ICatalog
from persistent import Persistent
from persistent.interfaces import IPersistent
from pyramid.events import subscriber
from zope.container.btree import BTreeContainer
from zope.container.contained import Contained
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent.interfaces import IObjectAddedEvent, IObjectRemovedEvent
from zope.schema.fieldproperty import FieldProperty

from pyams_catalog.index import KeywordIndexWithInterface
from pyams_catalog.query import CatalogResultSet
from pyams_security.interfaces import IViewContextPermissionChecker
from pyams_utils.adapter import ContextAdapter, adapter_config, get_annotation_adapter
from pyams_utils.container import SimpleContainerMixin
from pyams_utils.factory import factory_config
from pyams_utils.progress import init_progress_status, set_progress_status
from pyams_utils.registry import get_utility
from pyams_utils.request import query_request
from pyams_utils.zodb import volatile_property
from pyams_zfiles.interfaces import CATALOG_PROPERTIES_INDEXES_KEY, ICatalogPropertiesIndexesContainer, \
    ICatalogPropertiesIndexesContainerTarget, ICatalogPropertyIndex, IDocumentContainer, IDocumentVersion, \
    MANAGE_APPLICATION_PERMISSION

__docformat__ = 'restructuredtext'


class DocumentPropertyIndex(KeywordIndexWithInterface):
    """Document property index"""
    
    def __init__(self, property_name):
        self.property_name = property_name
        super().__init__(IDocumentVersion, discriminator=self.discriminator)
    
    def discriminator(self, obj, default):
        return obj.get_index_property(self.property_name, default)


@factory_config(ICatalogPropertyIndex)
class CatalogPropertyIndex(Persistent, Contained):
    """Catalog property index"""
    
    property_name = FieldProperty(ICatalogPropertyIndex['property_name'])


@adapter_config(required=ICatalogPropertyIndex,
                provides=IViewContextPermissionChecker)
class CatalogPropertyIndexPermissionChecker(ContextAdapter):
    """Catalog property index permission checker"""
    
    edit_permission = MANAGE_APPLICATION_PERMISSION


@subscriber(IObjectAddedEvent, context_selector=ICatalogPropertyIndex)
def handle_added_property_index(event):
    """Handle added property index"""
    property_name = event.object.property_name
    index = DocumentPropertyIndex(property_name)
    catalog = get_utility(ICatalog)
    catalog[f'zfile_property::{property_name}'] = index
    # update index names list
    container = get_utility(IDocumentContainer)
    del ICatalogPropertiesIndexesContainer(container).index_names
    # init progress status
    request = query_request()
    progress_id = request.params.get('progress_id', f'zfiles_property_index::{property_name}')
    init_progress_status(progress_id, request.principal.id,
                         f"ZFiles index updater: {property_name}")
    # update catalog new and old indexes
    try:
        intids = get_utility(IIntIds)
        source = catalog['zfile_properties']
        source_values = list(source.unique_values())
        progress_length = len(source_values)
        set_progress_status(progress_id, length=progress_length)
        for position, full_value in enumerate(source_values):
            name, value = full_value.split('=', 1)
            if name != property_name:
                continue
            for docid in list(source.applyEq(full_value)):
                document = intids.queryObject(docid)
                if document is not None:
                    index.reindex_doc(docid, document)
                    source.reindex_doc(docid, document)
            transaction.savepoint()
            set_progress_status(progress_id, length=progress_length, current=position)
    finally:
        set_progress_status(progress_id, 'finished')


@subscriber(IObjectRemovedEvent, context_selector=ICatalogPropertyIndex)
def handle_removed_property_index(event):
    """Handle removed property index"""
    property_name = event.object.property_name
    index_name = f'zfile_property::{property_name}'
    catalog = get_utility(ICatalog)
    source = catalog[index_name]
    target = catalog['zfile_properties']
    del catalog[index_name]
    # update index names list
    container = get_utility(IDocumentContainer)
    del ICatalogPropertiesIndexesContainer(container).index_names
    # update catalog new and old indexes
    intids = get_utility(IIntIds)
    for value in list(source.unique_values()):
        for docid in source.applyEq(value):
            document = intids.queryObject(docid)
            if document is not None:
                target.reindex_doc(docid, document)
        transaction.savepoint()


@factory_config(ICatalogPropertiesIndexesContainer)
class CatalogPropertyIndexContainer(SimpleContainerMixin, BTreeContainer):
    """Catalog properties indexes container"""
    
    def append(self, item: IPersistent, notify=True):
        del self.index_names
        super().append(item, notify)

    @volatile_property
    def index_names(self):
        """Indexes names getter"""
        return [
            index.property_name
            for index in self.values()
        ]
    
    def __delitem__(self, key):
        del self.index_names
        super().__delitem__(key)


@adapter_config(required=ICatalogPropertiesIndexesContainerTarget,
                provides=ICatalogPropertiesIndexesContainer)
def catalog_property_index_container(context):
    """Catalog properties indexes container adapter"""
    return get_annotation_adapter(context, CATALOG_PROPERTIES_INDEXES_KEY,
                                  ICatalogPropertiesIndexesContainer,
                                  name='++indexes++')
