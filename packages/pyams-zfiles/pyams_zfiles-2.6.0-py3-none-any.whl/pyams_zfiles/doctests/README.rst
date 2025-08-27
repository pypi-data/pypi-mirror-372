====================
PyAMS ZFiles package
====================


Introduction
------------

This package is composed of a set of utility functions, usable into any Pyramid application.

    >>> import tempfile
    >>> temp_dir = tempfile.mkdtemp()

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)
    >>> config.registry.settings['zodbconn.uri'] = 'file://{dir}/Data.fs?blobstorage_dir={dir}/blobs'.format(
    ...     dir=temp_dir)

    >>> import transaction
    >>> from pyramid_zodbconn import includeme as include_zodbconn
    >>> include_zodbconn(config)
    >>> from pyramid_rpc.xmlrpc import includeme as include_xmlrpc
    >>> include_xmlrpc(config)
    >>> from pyramid_rpc.jsonrpc import includeme as include_jsonrpc
    >>> include_jsonrpc(config)
    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)
    >>> from pyams_site import includeme as include_site
    >>> include_site(config)
    >>> from pyams_i18n import includeme as include_i18n
    >>> include_i18n(config)
    >>> from pyams_catalog import includeme as include_catalog
    >>> include_catalog(config)
    >>> from pyams_file import includeme as include_file
    >>> include_file(config)
    >>> from pyams_security import includeme as include_security
    >>> include_security(config)
    >>> from pyams_workflow import includeme as include_workflow
    >>> include_workflow(config)
    >>> from pyams_zmi import includeme as include_zmi
    >>> include_zmi(config)
    >>> from pyams_form import includeme as include_form
    >>> include_form(config)
    >>> from pyams_zfiles import includeme as include_zfiles
    >>> include_zfiles(config)

    >>> from pyams_site.generations import upgrade_site
    >>> request = DummyRequest()
    >>> app = upgrade_site(request)
    Upgrading PyAMS timezone to generation 1...
    Upgrading PyAMS I18n to generation 1...
    Upgrading PyAMS catalog to generation 1...
    Upgrading PyAMS file to generation 4...
    Upgrading PyAMS security to generation 2...
    Upgrading PyAMS ZFiles to generation 3...

    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> from zope.dublincore.interfaces import IZopeDublinCore
    >>> from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter
    >>> config.registry.registerAdapter(ZDCAnnotatableAdapter, (IAttributeAnnotatable, ), IZopeDublinCore)

    >>> from beaker.cache import CacheManager, cache_regions
    >>> cache = CacheManager(**{'cache.type': 'memory'})
    >>> cache_regions.update({'default': {'type': 'memory', 'expire': 3600}})
    >>> cache_regions.update({'persistent': {'type': 'memory', 'expire': 3600}})


Adding new documents
--------------------

    >>> from pyams_utils.registry import set_local_registry
    >>> set_local_registry(app.getSiteManager())

    >>> from pyams_utils.factory import create_object
    >>> from pyams_utils.registry import get_utility
    >>> from pyams_zfiles.interfaces import IDocumentContainer, ICatalogPropertyIndex, ICatalogPropertiesIndexesContainer

    >>> utility = get_utility(IDocumentContainer)
    >>> utility
    <pyams_zfiles.utility.DocumentContainer object at 0x...>

    >>> utility.oid_prefix = 'ZF:'

    >>> import base64
    >>> from pyams_security.principal import PrincipalInfo
    >>> encoded = base64.encodebytes(b'admin:admin').decode()
    >>> request = DummyRequest(headers={'Authorization': 'Basic {}'.format(encoded)})
    >>> request.principal = PrincipalInfo(id='system:admin')

    >>> from pyramid.threadlocal import manager
    >>> manager.push({'request': request, 'registry': config.registry})

    >>> data = b"This is my document content"
    >>> properties = {
    ...     'application_name': 'PyAMS test application',
    ...     'title': 'Test document',
    ...     'owner': 'admin:admin',
    ...     'filename': 'test.txt',
    ...     'created_time': '2024-01-01',
    ...     'tags': ['Tag 1', 'Tag 2'],
    ...     'properties': {'Custom 3': 'Value 3', 'Custom 4': 'Value 4;Value 5'},
    ...     'Custom 1': "Value 1",
    ...     'Custom 2': "Value 2"
    ... }
    >>> document = utility.add_document(data, properties, request)
    >>> transaction.commit()

    >>> document
    <pyams_zfiles.document.DocumentVersion object at 0x...>

    >>> oid = document.oid

    >>> from pprint import pprint
    >>> pprint(document.to_json())
    {'access_mode': 'private',
     'api': 'http://example.com/api/zfiles/rest/ZF:...',
     'application_name': 'PyAMS test application',
     'content_type': 'text/plain',
     'created_time': None,
     'creator': 'system:admin',
     'filename': 'test.txt',
     'filesize': 27,
     'hash': '04b251e9e34e6d58efde44ebafd7c769a630cdcf633c134af1e8b247100b6e774d3dccfe236e2b7ef96fbe829b3896128b201e0aa1079f99bc7ef532d58860aa',
     'href': 'http://example.com/++etc++site/ZFiles/2024/01/ZF:.../++versions++/1/++attr++data',
     'managers': [],
     'oid': 'ZF:...',
     'owner': 'admin:admin',
     'properties': {'Custom 1': 'Value 1', 'Custom 2': 'Value 2', 'Custom 3': 'Value 3', 'Custom 4': 'Value 4;Value 5'},
     'readers': [],
     'status': 'draft',
     'status_update_time': '...T...',
     'status_updater': 'system:admin',
     'tags': ['Tag 1', 'Tag 2'],
     'title': 'Test document',
     'update_mode': 'private',
     'updated_time': None,
     'updater': 'system:admin',
     'version': 1}

You can specify a restricted set of properties when asking for JSON content:

    >>> pprint(document.to_json(fields=['content_type', 'creator', 'status']))
    {'content_type': 'text/plain',
     'creator': 'system:admin',
     'status': 'draft'}

    >>> from pyams_workflow.interfaces import IWorkflow, IWorkflowStateLabel
    >>> from pyams_zfiles.interfaces import STATE

    >>> wf = config.registry.getAdapter(document, IWorkflow)
    >>> wf
    <pyams_zfiles.workflow.DocumentWorkflow object at 0x...>

    >>> label = config.registry.queryAdapter(wf, IWorkflowStateLabel, name=STATE.DRAFT.value)
    >>> label.get_label(document)
    'draft created on .../.../... at ...:...'


    >>> from pyams_utils.traversing import get_parent
    >>> from pyams_zfiles.interfaces import IDocumentFolder
    >>> folder = get_parent(document, IDocumentFolder)
    >>> folder
    <pyams_zfiles.folder.DocumentFolder object at 0x...>


Updating document
-----------------

    >>> properties = {
    ...     'status': 'published'
    ... }
    >>> document = utility.update_document(oid, properties=properties, request=request)
    >>> transaction.commit()

    >>> document.oid == oid
    True

    >>> pprint(document.to_json())
    {'access_mode': 'private',
     'api': 'http://example.com/api/zfiles/rest/ZF:...',
     'application_name': 'PyAMS test application',
     'content_type': 'text/plain',
     'created_time': None,
     'creator': 'system:admin',
     'filename': 'test.txt',
     'filesize': 27,
     'hash': '04b251e9e34e6d58efde44ebafd7c769a630cdcf633c134af1e8b247100b6e774d3dccfe236e2b7ef96fbe829b3896128b201e0aa1079f99bc7ef532d58860aa',
     'href': 'http://example.com/++etc++site/ZFiles/2024/01/ZF:.../++versions++/1/++attr++data',
     'managers': [],
     'oid': 'ZF:...',
     'owner': 'admin:admin',
     'properties': {'Custom 1': 'Value 1',
                    'Custom 2': 'Value 2',
                    'Custom 3': 'Value 3',
                    'Custom 4': 'Value 4;Value 5'},
     'readers': [],
     'status': 'published',
     'status_update_time': '...T...',
     'status_updater': 'system:admin',
     'tags': ['Tag 1', 'Tag 2'],
     'title': 'Test document',
     'update_mode': 'private',
     'updated_time': None,
     'updater': 'system:admin',
     'version': 1}

    >>> label = config.registry.queryAdapter(wf, IWorkflowStateLabel)
    >>> label.get_label(document)
    'published on .../.../... at ...:...'


Updating document content
-------------------------

    >>> data = b"New file content"
    >>> properties = {
    ...     'filename': 'modified.txt'
    ... }
    >>> document = utility.update_document(oid, data=data, properties=properties, request=request)
    >>> transaction.commit()

    >>> document.oid == oid
    True

    >>> pprint(document.to_json())
    {'access_mode': 'private',
     'api': 'http://example.com/api/zfiles/rest/ZF:...',
     'application_name': 'PyAMS test application',
     'content_type': 'text/plain',
     'created_time': None,
     'creator': 'system:admin',
     'filename': 'modified.txt',
     'filesize': 16,
     'hash': 'a4cf7ce7d511c577ea9d450e11cc7fa17d571f883c0a182b308242197b784c9f5645257b6873776a3f845a5fa9d84935685de602b47faedc9f837ddb169ad678',
     'href': 'http://example.com/++etc++site/ZFiles/2024/01/ZF:.../++versions++/2/++attr++data',
     'managers': [],
     'oid': 'ZF:...',
     'owner': 'admin:admin',
     'properties': {'Custom 1': 'Value 1',
                    'Custom 2': 'Value 2',
                    'Custom 3': 'Value 3',
                    'Custom 4': 'Value 4;Value 5'},
     'readers': [],
     'status': 'draft',
     'status_update_time': '...T...',
     'status_updater': 'system:admin',
     'tags': ['Tag 1', 'Tag 2'],
     'title': 'Test document',
     'update_mode': 'private',
     'updated_time': None,
     'updater': 'system:admin',
     'version': 2}

    >>> label = config.registry.queryAdapter(wf, IWorkflowStateLabel, name=STATE.DRAFT.value)
    >>> label.get_label(document)
    'new version created on .../.../... at ...:...'


Getting document
----------------

You can get a document from it's OID; by default, it's the last version which is returned:

    >>> document = utility.get_document(oid)
    >>> document.to_json().get('version')
    2

But you can specify a specific version or a specific workflow status:

    >>> document = utility.get_document(oid, version=1)
    >>> document.to_json().get('version')
    1

    >>> document = utility.get_document(oid, status=STATE.PUBLISHED.value)
    >>> document.to_json().get('version')
    1


Searching documents
-------------------

Empty queries always return an empty results list:

    >>> list(utility.find_documents({}))
    []

The same rule applies to queries only containing null values:

    >>> list(utility.find_documents({'status': None, 'properties': None}))
    []

Except if requested explicitly, documents search only return published documents:

    >>> documents = utility.find_documents({'application_name': 'PyAMS test application'})
    >>> pprint(list(map(lambda x: x.to_json().get('version'), documents)))
    [1]

Anyway, you can search documents on any attribute, property or tag:

    >>> documents = utility.find_documents({'properties': {'Custom 1': 'Value 1'}})
    >>> len(list(documents))
    1

    >>> documents = utility.find_documents({'tags': 'Tag 1'})
    >>> len(list(documents))
    1

Attributes can be combined, using an "and" operator:

    >>> documents = utility.find_documents({'properties': {'Custom 1': 'Value 1'}, 'tags': 'Tag 1'})
    >>> len(list(documents))
    1

If you want to get documents matching several values for a same property, you have to use
URL params encoding; in this case, several values for a same property are combined with an "or":

    >>> documents = utility.find_documents({'properties': 'Custom 1=Value 1&Custom 1=Value 2'})
    >>> len(list(documents))
    1

Extra properties which are not from base document properties are automatically included into
*properties*:

    >>> documents = utility.find_documents({'Custom 1': 'Value 1'})
    >>> len(list(documents))
    1

When defining "multi-values" properties separated with semicolons, you can search documents by individual
values:

    >>> documents = utility.find_documents({'Custom 4': 'Value 4'})
    >>> len(list(documents))
    1

Dates parameters are using *ranges*, which are two values tuples containing the start and the
end dates of the requested period, each of which can be *None*; results list is empty because
documents don't have creation date:

    >>> from datetime import datetime, timedelta
    >>> begin = datetime.utcnow() - timedelta(minutes=1)
    >>> documents = utility.find_documents({'created_date': [begin, None]})
    >>> len(list(documents))
    0

    >>> end = begin + timedelta(minutes=1)
    >>> documents = utility.find_documents({'created_date': [begin, end]})
    >>> len(list(documents))
    0

    >>> documents = utility.find_documents({'created_date': [None, end]})
    >>> len(list(documents))
    0


Properties indexes
------------------

We can create custom properties indexes. These indexes dedicated to a given property can reduce
the "properties" index size and the probability of database conflicts on write.

Adding or removing a new property index required reindexing of the new property index as weel as the previous
common properties index, which can be quite long if you have many documents!

    >>> from zope.lifecycleevent import ObjectAddedEvent, ObjectRemovedEvent
    >>> from hypatia.interfaces import ICatalog
    >>> from pyams_zfiles.index import DocumentPropertyIndex

    >>> indexes = ICatalogPropertiesIndexesContainer(utility)
    >>> index = create_object(ICatalogPropertyIndex)
    >>> index.property_name = 'Custom 4'
    >>> indexes.append(index)
    >>> request.registry.notify(ObjectAddedEvent(index, indexes))

    >>> catalog = get_utility(ICatalog)
    >>> catalog.get('zfile_property::Custom 4')
    <pyams_zfiles.index.DocumentPropertyIndex object at 0x... oid 0x... in <ZODB.Connection.Connection object at 0x...>>

    >>> documents = utility.find_documents({'Custom 4': 'Value 4'})
    >>> len(list(documents))
    1

    >>> del indexes[index.__name__]
    >>> request.registry.notify(ObjectRemovedEvent(index, indexes))

    >>> catalog.get('zfile_property::Custom 4') is None
    True

    >>> documents = utility.find_documents({'Custom 4': 'Value 4'})
    >>> len(list(documents))
    1


Deleting documents
------------------

    >>> document = utility.delete_document(oid, request=None)
    >>> list(folder.keys())
    []


Properties extractors
---------------------

Extractors are components which can be used to extract a document properties from it's internal content.
The first step is to have an IDocumentExtractor which can be used to convert document content into a basic
text representation on which we will apply regular expressions to extract properties:

    >>> import os
    >>> import base64
    >>> from pyams_zfiles.tests.test_utilsdocs import CURRENT_DIR

    >>> path = os.path.join(CURRENT_DIR, '..', 'doctests', 'data', 'document.txt')
    >>> with open(path, 'rb') as datafile:
    ...     data = datafile.read()
    >>> properties = {
    ...     'application_name': 'PyAMS test application',
    ...     'title': 'Test document',
    ...     'owner': 'admin:admin',
    ...     'filename': 'document.txt',
    ...     'properties': {'Custom 1': 'Value 1'},
    ...     'created_time': '2024-01-01'
    ... }
    >>> document = utility.add_document(data, properties, request)
    >>> transaction.commit()

    >>> from pyams_zfiles.interfaces import IDocumentExtractor, IDocumentPropertyExtractorInfo, IDocumentPropertyExtractorContainer

    >>> extractor_info = create_object(IDocumentPropertyExtractorInfo)
    >>> extractor_info.name = 'Filter 1'
    >>> extractor_info.property_name = 'document_id'
    >>> extractor_info.regex = " - document_id: ([a-zA-Z0-9]+)"
    >>> extractor_info.application_names = ['PyAMS test application']

    >>> container = IDocumentPropertyExtractorContainer(utility)
    >>> container_name = container.append(extractor_info)

    >>> new_properties = container.extract_properties(document)
    >>> new_properties
    {'document_id': '0x123456'}

    >>> extractor_info = create_object(IDocumentPropertyExtractorInfo)
    >>> extractor_info.name = 'Filter 2'
    >>> extractor_info.property_name = 'version_id'
    >>> extractor_info.regex = " - version_id: ([a-z]+)"
    >>> container_name = container.append(extractor_info)

    >>> new_properties = container.extract_properties(document)
    >>> pprint(new_properties)
    {'document_id': '0x123456',
     'version_id': 'abcdef'}

    >>> extractor_info.active = False
    >>> new_properties = container.extract_properties(document)
    >>> pprint(new_properties)
    {'document_id': '0x123456'}

    >>> extractor_info = create_object(IDocumentPropertyExtractorInfo)
    >>> extractor_info.name = 'Filter 3'
    >>> extractor_info.properties = {'Custom 1': 'Value 1'}
    >>> extractor_info.property_name = 'multiple_id'
    >>> extractor_info.regex = r" - multiple_key: ([a-zA-Z0-9\s]+)\n"
    >>> container_name = container.append(extractor_info)

    >>> new_properties = container.extract_properties(document)
    >>> pprint(new_properties)
    {'document_id': '0x123456', 'multiple_id': 'value 1;value 2'}

We can disable searching of all occurrences of our regexp to only extract the first value:

    >>> extractor_info.search_all_occurrences = False

    >>> new_properties = container.extract_properties(document)
    >>> pprint(new_properties)
    {'document_id': '0x123456', 'multiple_id': 'value 1'}

    >>> extractor_info.search_all_occurrences = True


We now create another extractor which doesn't match our document:

    >>> extractor_info = create_object(IDocumentPropertyExtractorInfo)
    >>> extractor_info.name = 'Filter 4'
    >>> extractor_info.properties = {'Custom 1': 'Value 2'}
    >>> extractor_info.property_name = 'multiple_id'
    >>> extractor_info.regex = r" - multiple_key: ([a-zA-Z0-9\s]+)\n"
    >>> container_name = container.append(extractor_info)

We can now create a new document from scratch:

    >>> document = utility.add_document(data, properties, request)
    >>> transaction.commit()

    >>> pprint(document.to_json().get('properties'))
    {'Custom 1': 'Value 1',
     'document_id': '0x123456',
     'multiple_id': 'value 1;value 2'}


Dynamic attributes
------------------

We can set some file attributes values, as *title* and *filename*, with values which can
be defined dynamically based on other document properties:

    >>> from datetime import datetime, timezone
    >>> now = datetime.now(timezone.utc)

    >>> with open(path, 'rb') as datafile:
    ...     data = datafile.read()
    >>> properties = {
    ...     'application_name': 'PyAMS test application',
    ...     'title': 'Test document {Custom 5}',
    ...     'owner': 'admin:admin',
    ...     'filename': 'document-{now:%Y%m%d}.txt',
    ...     'properties': {'Custom 5': 'Value 5'}
    ... }
    >>> document = utility.add_document(data, properties, request)
    >>> document.to_json().get('title')
    'Test document Value 5'
    >>> document.to_json().get('filename') == f'document-{now:%Y%m%d}.txt'
    True


Tests cleanup:

    >>> set_local_registry(None)
    >>> tearDown()
