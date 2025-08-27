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

"""PyAMS_zfiles.folder module

This module just defines documents folder class.
"""

from zope.container.folder import Folder

from pyams_utils.factory import factory_config
from pyams_zfiles.interfaces import IDocumentFolder


__docformat__ = 'restructuredtext'


@factory_config(IDocumentFolder)
class DocumentFolder(Folder):
    """Documents folder class

    These folders are created for each year and each month to store documents.
    """
