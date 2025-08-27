#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS zfiles.interfaces module

This module defines ZFiles global package interfaces.
"""

from enum import Enum

from zope.container.constraints import containers, contains
from zope.container.interfaces import IBTreeContainer
from zope.interface import Attribute, Interface, implementer
from zope.schema import Bool, Choice, Dict, List, Password, Text, TextLine
from zope.schema.interfaces import IDict
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from pyams_file.schema import FileField
from pyams_security.interfaces import IContentRoles
from pyams_security.schema import PrincipalField, PrincipalsSetField
from pyams_workflow.interfaces import IWorkflow, IWorkflowManagedContent, IWorkflowPublicationSupport

__docformat__ = 'restructuredtext'

from pyams_zfiles import _


#
# API endpoints
#

REST_CONTAINER_ROUTE = 'pyams_zfiles.rest.container'
'''ZFiles container REST API route name'''

REST_CONTAINER_PATH = '/api/zfiles/rest'
'''ZFiles container REST API default path'''

REST_DOCUMENT_ROUTE = 'pyams_zfiles.rest.document'
'''ZFiles document REST API route name'''

REST_DOCUMENT_PATH = '/api/zfiles/rest/{oid}*version'
'''ZFiles document REST API default path'''

REST_SYNCHRONIZER_ROUTE = 'pyams_zfiles.rest.synchronizer'
'''ZFiles synchronizer REST API route name'''

REST_SYNCHRONIZER_PATH = '/api/zfiles/rest/synchronize'
'''ZFiles synchronizer REST API default path'''

GRAPHQL_API_ROUTE = 'pyams_zfiles.graphql'
'''ZFiles GraphQL API route name'''

GRAPHQL_API_PATH = '/api/zfiles/graphql'
'''ZFiles GraphQL API default path'''

JSONRPC_ENDPOINT = 'pyams_zfiles.jsonrpc'
'''ZFiles JSON-RPC endpoint name'''

JSONRPC_PATH = '/api/zfiles/jsonrpc'
'''ZFiles JSON-RPC default path'''

XMLRPC_ENDPOINT = 'pyams_zfiles.xmlrpc'
'''ZFiles XML-RPC endpoint name'''

XMLRPC_PATH = '/api/zfiles/xmlrpc'
'''ZFiles XML-RPC default path'''


#
# Global application strings
#

PYAMS_ZFILES_SKIN_NAME = 'PyAMS.zfiles.skin'
'''Custom ZFiles skin name'''


PYAMS_ZFILES_APPLICATIONS_VOCABULARY = 'PyAMS.zfiles.applications'
'''Name of registered applications vocabulary'''


#
# ZFiles permissions
#

MANAGE_APPLICATION_PERMISSION = 'pyams.ManageZfilesApplication'
'''Permission required to manage ZFiles application'''

CREATE_DOCUMENT_PERMISSION = 'pyams.CreateDocument'
'''Permission required to create a new document'''

CREATE_DOCUMENT_WITH_OWNER_PERMISSION = 'pyams.CreateDocumentWithOwner'
'''Permission required to create a new document with a specific owner'''

MANAGE_DOCUMENT_PERMISSION = 'pyams.ManageDocument'
'''Permission required to manage document properties'''

READ_DOCUMENT_PERMISSION = 'pyams.ReadDocument'
'''Permission required to view document'''

SYNCHRONIZE_PERMISSION = 'pyams.Synchronize'
'''Permission required to call synchronization on a specific configuration'''


ZFILES_ADMIN_ROLE = 'pyams.DocumentsAdministrator'
'''ZFiles application administrator role'''

ZFILES_IMPORTER_ROLE = 'pyams.DocumentsImporter'
'''Documents importer role'''

ZFILES_CREATOR_ROLE = 'pyams.DocumentCreator'
'''Document creator role'''

ZFILES_MANAGER_ROLE = 'pyams.DocumentsManager'
'''Documents manager role'''

ZFILES_OWNER_ROLE = 'pyams.DocumentOwner'
'''Document owner role'''

ZFILES_READER_ROLE = 'pyams.DocumentReader'
'''Document reader role'''

ZFILES_SYNCHRONIZER_ROLE = 'pyams.Synchronizer'
'''Document synchronizer role'''


#
# Documents interfaces
#

ZFILES_WORKFLOW_NAME = 'pyams_zfiles.workflow'


class IDocumentWorkflow(IWorkflow):
    """Document workflow marker interface"""


class STATE(Enum):
    """State modes"""
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'
    DELETED = 'deleted'


STATES_VALUES = tuple(map(lambda x: x.value, STATE))


STATE_LABELS = {
    STATE.DRAFT.value: _("Draft"),
    STATE.PUBLISHED.value: _("Published"),
    STATE.ARCHIVED.value: _("Archived"),
    STATE.DELETED.value: _("Deleted")
}

STATES_HEADERS = {
    STATE.DRAFT.value: _("draft created"),
    STATE.PUBLISHED.value: _("published"),
    STATE.ARCHIVED.value: _("archived")
}

STATES_VOCABULARY = SimpleVocabulary([
    SimpleTerm(i, title=t)
    for i, t in STATE_LABELS.items()
])


class ACCESS_MODE(Enum):
    """Security policy access modes"""
    PRIVATE = 'private'
    PROTECTED = 'protected'
    PUBLIC = 'public'

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, int):
            try:
                return list(ACCESS_MODE)[value]
            except IndexError:
                pass
        raise ValueError("%r is not a valid %s" % (value, cls.__name__))


# Keep for compatibility reason
AccessMode = ACCESS_MODE


ACCESS_MODE_LABELS = {
    ACCESS_MODE.PRIVATE.value: _("Private"),
    ACCESS_MODE.PROTECTED.value: _("Protected"),
    ACCESS_MODE.PUBLIC.value: _("Public")
}


ACCESS_MODE_VOCABULARY = SimpleVocabulary([
    SimpleTerm(i, title=t)
    for i, t in ACCESS_MODE_LABELS.items()
])


class IPropertiesField(IDict):
    """Properties schema field interface"""


@implementer(IPropertiesField)
class PropertiesField(Dict):
    """Properties schema field"""

    def __init__(self, *args, **kwargs):
        super().__init__(key_type=TextLine(),
                         value_type=TextLine(),
                         *args, **kwargs)


class IDocumentVersion(IWorkflowPublicationSupport):
    """Document version interface"""

    oid = TextLine(title="Document OID",
                   description=_("Document unique identifier"),
                   readonly=True)

    title = TextLine(title=_("Document title"),
                     description=_("User friendly name of the document"),
                     required=True)

    application_name = TextLine(title=_("Source application name"),
                                description=_("Name of the application which submitted "
                                              "the document"),
                                required=True)

    data = FileField(title=_("Document data"),
                     description=_("This is where document content is stored"),
                     required=True)

    hash = TextLine(title=_("Document data hash"),
                    description=_("This unique signature is built using SHA512 algorithm"),
                    required=True)

    access_mode = Choice(title=_("Access mode"),
                         description=_("Access mode on this document"),
                         required=True,
                         vocabulary=ACCESS_MODE_VOCABULARY,
                         default=ACCESS_MODE.PRIVATE.value)

    update_mode = Choice(title=_("Update mode"),
                         description=_("Update mode on this document"),
                         required=True,
                         vocabulary=ACCESS_MODE_VOCABULARY,
                         default=ACCESS_MODE.PRIVATE.value)

    properties = PropertiesField(title=_("Properties"),
                                 description=_("List of free additional properties which can be "
                                               "applied to the document; these properties can't "
                                               "be used for searching"),
                                 required=False)

    index_properties = Attribute("Properties value used for indexing")

    tags = List(title=_("Document tags"),
                description=_("List of free additional tags which can be applied to the "
                              "document; these tags can be used for searching"),
                value_type=TextLine(),
                required=False)

    updater = PrincipalField(title=_("Last document updater"),
                             description=_("Name of the last principal which updated the "
                                           "document"),
                             required=True)

    def update(self, data, properties, request=None):
        """Set document data and properties"""

    def update_status(self, properties, request=None):
        """Update document status"""

    def to_json(self, request=None):
        """Get document properties in JSON format"""


class IDocumentRoles(IContentRoles):
    """Document roles interface"""

    creator = PrincipalField(title=_("Document creator"),
                             description=_("Name of the principal which created the document"),
                             role_id=ZFILES_CREATOR_ROLE,
                             required=True)

    owner = PrincipalField(title=_("Document owner"),
                           description=_("Name of the principal which is owner of the document"),
                           role_id=ZFILES_OWNER_ROLE,
                           required=True)

    readers = PrincipalsSetField(title=_("Document readers"),
                                 description=_("Name of principals allowed to read the document"),
                                 role_id=ZFILES_READER_ROLE,
                                 required=False)

    managers = PrincipalsSetField(title=_("Document managers"),
                                  description=_("Name of principals allowed to update the "
                                                "document"),
                                  role_id=ZFILES_MANAGER_ROLE,
                                  required=False)


class IDocument(IWorkflowManagedContent):
    """Document interface"""

    containers('.IDocumentFolder')

    oid = TextLine(title="Document OID",
                   description=_("Document unique identifier"),
                   readonly=True)

    def get_oid(self):
        """Generate new unique ID"""


class IDocumentFolder(IBTreeContainer):
    """Document folder interface"""

    containers('.IDocumentContainer', '.IDocumentFolder')
    contains(IDocument, '.IDocumentFolder')


DOCUMENT_CONTAINER_NAME = 'ZFiles'
'''ZFiles documents container name'''


class IDocumentContainer(IBTreeContainer):
    """Document container utility interface"""

    contains(IDocumentFolder)

    oid_prefix = TextLine(title=_("Documents OID prefix"),
                          description=_("Prefix used to identify documents which were "
                                        "created locally (unlike documents which were created "
                                        "into another documents container and synchronized with "
                                        "this container)"),
                          required=False)

    show_home_menu = Bool(title=_("Access menu from home"),
                          description=_("If 'yes', a menu will be displayed to get access to "
                                        "documents container from site admin home page"),
                          required=True,
                          default=False)

    def add_document(self, data, properties, request):
        """Add new document"""

    def import_document(self, oid, data, properties, request):
        """Import document from outer ZFiles database"""

    def find_documents(self, params, request=None):
        """Find documents matching given params"""

    def get_document(self, oid, version=None):
        """Retrieve existing document from it's OID

        If no version number is specified, the last version
        is returned.
        """

    # pylint: disable=too-many-arguments
    def update_document(self, oid, version=None, data=None, properties=None, request=None,
                        check_permission=True):
        """Update document data or properties"""

    def delete_document(self, oid):
        """Delete document or version"""


class IDocumentContainerRoles(IContentRoles):
    """Document container utility roles interface"""

    application_managers = PrincipalsSetField(title=_("Application managers"),
                                              description=_("These principals can only "
                                                            "manage application properties; "
                                                            "documents manager role is required "
                                                            "to manage documents!"),
                                              role_id=ZFILES_ADMIN_ROLE,
                                              required=False)

    documents_creators = PrincipalsSetField(title=_("Documents creators"),
                                            description=_("These principals will be allowed to "
                                                          "create or import new documents"),
                                            role_id=ZFILES_IMPORTER_ROLE,
                                            required=False)

    documents_managers = PrincipalsSetField(title=_("Documents managers"),
                                            description=_("These principals will be allowed to "
                                                          "manage any document properties"),
                                            role_id=ZFILES_MANAGER_ROLE,
                                            required=False)

    documents_readers = PrincipalsSetField(title=_("Documents readers"),
                                           description=_("These principals will be allowed to "
                                                         "read any document properties"),
                                           role_id=ZFILES_READER_ROLE,
                                           required=False)


class DocumentContainerError(Exception):
    """Base document container error"""


#
# Documents synchronizer interface
#

IMPORT_MODE = 'import'
EXPORT_MODE = 'export'
DELETE_MODE = 'delete'


class SynchronizerStatus(Enum):
    """Synchronizer document status"""
    MISSING_CONFIGURATION = 'MISSING_CONFIGURATION'
    FORBIDDEN = 'FORBIDDEN'
    NOT_FOUND = 'NOT_FOUND'
    NO_DATA = 'NO_DATA'
    ERROR = 'ERROR'
    OK = 'OK'


DOCUMENT_SYNCHRONIZER_KEY = 'pyams_zfiles.synchronizer'

DEFAULT_CONFIGURATION_NAME = 'default'


class IDocumentSynchronizerConfiguration(Interface):
    """Document synchronizer configuration interface"""

    name = TextLine(title=_("Configuration name"),
                    description=_("Unique name of the configuration"),
                    required=True,
                    default=DEFAULT_CONFIGURATION_NAME)

    target = TextLine(title=_("Remote XML-RPC endpoint"),
                      description=_("URL of the remote documents container XML-RPC endpoint "
                                    "used for synchronization"),
                      required=False)

    username = TextLine(title=_("User name"),
                        description=_("Name of the remote user used for synchronization"),
                        required=False)

    password = Password(title=_("Password"),
                        description=_("Password of the remote user used for synchronization"),
                        required=False)

    mode = Choice(title=_("Synchronization mode"),
                  description=_("Synchronization mode used for synchronization"),
                  required=True,
                  vocabulary=SimpleVocabulary([
                      SimpleTerm(value=EXPORT_MODE, title=_("Export mode")),
                      SimpleTerm(value=IMPORT_MODE, title=_("Import mode"))
                  ]),
                  default=EXPORT_MODE)
    
    enabled = Bool(title=_("Enabled configuration"),
                   description=_("If 'no', this configuration will not be usable for "
                                 "synchronization"),
                   required=True,
                   default=True)

    def get_client(self):
        """Remote XML-RPC client getter"""


class IDocumentSynchronizerConfigurationRoles(IContentRoles):
    """Document synchronizer configuration roles interface"""

    users = PrincipalsSetField(title=_("Configuration users"),
                               description=_("Principals which are granted permission to "
                                             "call this configuration"),
                               role_id=ZFILES_SYNCHRONIZER_ROLE,
                               required=False)


class IDocumentSynchronizer(IBTreeContainer):
    """Documents synchronizer interface"""

    contains(IDocumentSynchronizerConfiguration)

    def push(self, oid, mode=IMPORT_MODE, request=None, configuration=None):
        """Push document with given OID to remote container"""
        
    def pull(self, oid, mode=IMPORT_MODE, request=None, configuration=None):
        """Get document with given OID from remote container"""

    def synchronize_all(self, imported=None, deleted=None, request=None, configuration=None):
        """Synchronize all imported and deleted OIDs with remote container"""


#
# Custom catalog properties indexes
#

CATALOG_PROPERTIES_INDEXES_KEY = 'pyams_zfiles.catalog.indexes'


class ICatalogPropertyIndex(Interface):
    """Catalog property index interface"""
    
    property_name = TextLine(title=_("Property name"),
                             description=_("Name of the property used to create index"),
                             required=True)


class ICatalogPropertiesIndexesContainer(IBTreeContainer):
    """Catalog properties indexes container interface"""
    
    contains(ICatalogPropertyIndex)
    
    index_names = Attribute("List of properties indexes names")


class ICatalogPropertiesIndexesContainerTarget(Interface):
    """Catalog properties indexes container target marker interface"""


#
# Custom documents extraction tools
#

DOCUMENT_EXTRACTORS_KEY = 'pyams_zfiles.extractors'


class IDocumentExtractor(Interface):
    """Document extractor adapter interface"""

    def extract(self, pages=None):
        """Extract text from document content
        
        If set, *pages* is a tuple which specifies the 0-based list of document pages for which
        text is requested.
        """


class IDocumentPropertyExtractorInfo(Interface):
    """Document property extractor interface"""

    name = TextLine(title=_("Extractor name"),
                    description=_("Unique name of the properties extractor"),
                    required=True)

    active = Bool(title=_("Active extractor?"),
                  description=_("Uncheck this option to disable this extractor..."),
                  required=True,
                  default=True)

    property_name = TextLine(title=_("Property name"),
                             description=_("Name of the property which should be set by this extractor"),
                             required=True)

    override = Bool(title=_("Override current value?"),
                    description=_("If 'yes', the property will be extracted even if it is already defined "
                                  "into current document properties"),
                    required=True,
                    default=False)

    regex = Text(title=_("Extractor RegEx"),
                 description=_("Regular expression to use to extract property value from document content; "
                               "if the expression returns several results from the document content, "
                               "they will be set as a list in document properties"),
                 required=True)

    multiline = Bool(title=_("Multiline?"),
                     description=_("If 'yes', given expression will use RegExp MULTILINE option"),
                     required=True,
                     default=False)

    search_all_occurrences = Bool(title=_("Search for all occurrences?"),
                                  description=_("If 'yes', all occurrences will be extracted; otherwise, only the first "
                                                "occurrence will be extracted"),
                                  required=True,
                                  default=True)

    application_names = List(title=_("Selected applications"),
                             description=_("List of applications for which this extractor should be applied"),
                             value_type=Choice(vocabulary=PYAMS_ZFILES_APPLICATIONS_VOCABULARY),
                             required=False)

    properties = Dict(title=_("Selected properties"),
                      description=_("List of current document properties for which this extractor should be applied; "
                                    "you can define properties using the \"name=value\" syntax, with a newline "
                                    "between each property"),
                      key_type=TextLine(title=_("Property name")),
                      value_type=TextLine(title=_("Property value")),
                      required=False)

    def matches(self, document):
        """Check if extractor is matching given document"""

    def apply(self, content):
        """Apply extractor Regex to given content"""


class IDocumentPropertyExtractorContainer(IBTreeContainer):
    """Document properties extractor container interface"""

    contains(IDocumentPropertyExtractorInfo)

    def get_active_items(self):
        """Get iterator over active items"""

    def extract_properties(self, document, force=False):
        """Extract properties values for given document"""


class IDocumentPropertyExtractorContainerTarget(Interface):
    """Document property extractor container target marker interface"""
