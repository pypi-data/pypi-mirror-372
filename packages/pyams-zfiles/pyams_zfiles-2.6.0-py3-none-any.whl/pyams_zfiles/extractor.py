# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

import pypdf
import re
from io import BytesIO
from persistent import Persistent
from zope.container.btree import BTreeContainer
from zope.container.contained import Contained
from zope.location.interfaces import ISublocations
from zope.schema.fieldproperty import FieldProperty
from zope.traversing.interfaces import ITraversable

from pyams_file.interfaces import IFile
from pyams_security.interfaces import IViewContextPermissionChecker
from pyams_utils.adapter import ContextAdapter, adapter_config, get_annotation_adapter
from pyams_utils.container import SimpleContainerMixin
from pyams_utils.dict import update_dict
from pyams_utils.factory import factory_config
from pyams_utils.registry import get_pyramid_registry
from pyams_zfiles.interfaces import DOCUMENT_EXTRACTORS_KEY, IDocumentExtractor, IDocumentPropertyExtractorContainer, \
    IDocumentPropertyExtractorContainerTarget, IDocumentPropertyExtractorInfo, IDocumentVersion, \
    MANAGE_APPLICATION_PERMISSION

__docformat__ = 'restructuredtext'


@factory_config(IDocumentPropertyExtractorInfo)
class DocumentPropertyExtractorInfo(Persistent, Contained):
    """Document property extractor persistent class"""
    
    name = FieldProperty(IDocumentPropertyExtractorInfo['name'])
    active = FieldProperty(IDocumentPropertyExtractorInfo['active'])
    property_name = FieldProperty(IDocumentPropertyExtractorInfo['property_name'])
    override = FieldProperty(IDocumentPropertyExtractorInfo['override'])
    regex = FieldProperty(IDocumentPropertyExtractorInfo['regex'])
    multiline = FieldProperty(IDocumentPropertyExtractorInfo['multiline'])
    search_all_occurrences = FieldProperty(IDocumentPropertyExtractorInfo['search_all_occurrences'])
    application_names = FieldProperty(IDocumentPropertyExtractorInfo['application_names'])
    properties = FieldProperty(IDocumentPropertyExtractorInfo['properties'])

    def matches(self, document, force=False):
        """Check if extractor is matching given document"""
        version = IDocumentVersion(document, None)
        if version is None:
            return False
        if force:
            return True
        if self.application_names and (version.application_name not in self.application_names):
            return False
        properties = version.properties
        if (not self.override) and (properties or {}).get(self.property_name):
            return False
        if self.properties:
            if not properties:
                return False
            for key, value in self.properties.items():
                if properties.get(key) != value:
                    return False
        return True

    def apply(self, content):
        """Apply Regex to given content"""
        flags = 0
        if '\n' in self.regex:
            flags |= re.VERBOSE
        if self.multiline:
            flags |= re.MULTILINE
        expr = re.compile(self.regex, flags)
        values = None
        if self.search_all_occurrences:
            values = expr.findall(content)
        else:
            match = expr.search(content)
            if match:
                values = match.groups()
        if values:
            return {
                self.property_name: ';'.join(values)
            }
        return None


@adapter_config(required=IDocumentPropertyExtractorInfo,
                provides=IViewContextPermissionChecker)
class DocumentPropertyExtractorPermissionChecker(ContextAdapter):
    """Document property extractor permission checker"""
    
    edit_permission = MANAGE_APPLICATION_PERMISSION
    

@factory_config(IDocumentPropertyExtractorContainer)
class DocumentPropertyExtractorContainer(SimpleContainerMixin, BTreeContainer):
    """Document property extractors container class"""

    def get_active_items(self):
        """Get iterator over active items"""
        yield from filter(lambda x: IDocumentPropertyExtractorInfo(x).active,
                          self.values())

    def extract_properties(self, document, force=False):
        """Extract properties from given document"""
        extractor = IDocumentExtractor(document, None)
        if extractor is None:
            return None
        result = {}
        content = None
        for filter in self.get_active_items():
            if not filter.matches(document, force=force):
                continue
            if content is None:
                content = extractor.extract()
            for key, value in (filter.apply(content) or {}).items():
                update_dict(result, key, value)
        return result


@adapter_config(required=IDocumentPropertyExtractorContainerTarget,
                provides=IDocumentPropertyExtractorContainer)
def document_property_extractor_container(context):
    """Document property extractor container factory"""
    return get_annotation_adapter(context, DOCUMENT_EXTRACTORS_KEY,
                                  IDocumentPropertyExtractorContainer,
                                  name='++extractors++')
    
    
@adapter_config(name='extractors',
                required=IDocumentPropertyExtractorContainerTarget,
                provides=ITraversable)
class DocumentPropertyExtractorContainerTraverser(ContextAdapter):
    """Document property extractor container traverser"""
    
    def traverse(self, name, furtherPath=None):
        return IDocumentPropertyExtractorContainer(self.context)


@adapter_config(name='extractors',
                required=IDocumentPropertyExtractorContainerTarget,
                provides=ISublocations)
class DocumentPropertyExtractorsContainerSublocations(ContextAdapter):
    """Document property extractor container sublocations"""

    def sublocations(self):
        yield from IDocumentPropertyExtractorContainer(self.context).values()


@adapter_config(required=IDocumentVersion,
                provides=IDocumentExtractor)
def get_document_extractor(context):
    """Document extractor adapter"""
    return IDocumentExtractor(context.data, None)


@adapter_config(required=IFile,
                provides=IDocumentExtractor)
def get_file_extractor(context):
    """File extractor adapter"""
    if not (context and context.content_type):
        return None
    content_type = context.content_type
    if ';' in content_type:
        content_type, _ = context.content_type.split(';', 1)
    registry = get_pyramid_registry()
    extractor = registry.queryAdapter(context, IDocumentExtractor, name=content_type)
    if extractor is None:
        major, minor = content_type.split('/')
        extractor = registry.queryAdapter(context, IDocumentExtractor, name=f'{major}/*')
    return extractor
    

@adapter_config(name='text/*',
                required=IFile,
                provides=IDocumentExtractor)
class TextFileDocumentExtractor(ContextAdapter):
    """Text file document extractor"""
    
    def extract(self, pages=None):
        return self.context.data.decode()


@adapter_config(name='application/pdf',
                required=IFile,
                provides=IDocumentExtractor)
class PdfFileDocumentExtractor(ContextAdapter):
    """PDF file document extractor"""
    
    def extract(self, pages=None):
        reader = pypdf.PdfReader(BytesIO(self.context.data))
        if not pages:
            pages = (0,)
        output = ''
        for index in pages:
            output += reader.pages[index].extract_text()
        return output
