# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from pyams_table.interfaces import ITable

__docformat__ = 'restructuredtext'


class ICatalogPropertiesIndexesTable(ITable):
    """Catalog properties index table marker interface"""


class IDocumentPropertiesExtractorsTable(ITable):
    """Document properties extractors table marker interface"""
