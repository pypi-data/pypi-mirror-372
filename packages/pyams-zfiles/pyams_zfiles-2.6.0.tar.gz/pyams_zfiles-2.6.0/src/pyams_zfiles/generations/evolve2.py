#
# Copyright (c) 2015-2023 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_zfiles.generations.evolve2 module

This module handles ZFiles migration to generation 3.
"""

__docformat__ = 'restructuredtext'

from enum import Enum

import transaction

from pyams_utils.finder import find_objects_providing
from pyams_utils.registry import get_local_registry, query_utility, set_local_registry
from pyams_workflow.interfaces import IWorkflowVersions
from pyams_zfiles.interfaces import ACCESS_MODE, IDocument, IDocumentContainer, IDocumentVersion


def evolve(site):
    """Evolve 2: update access and update modes"""
    registry = get_local_registry()
    try:
        set_local_registry(site.getSiteManager())
        container = query_utility(IDocumentContainer)
        if container is not None:
            modes = list(ACCESS_MODE)
            for index, document in enumerate(find_objects_providing(container, IDocument)):
                print('.', end='')
                for version in IWorkflowVersions(document).get_versions():
                    access_mode = version.access_mode
                    if isinstance(access_mode, int):
                        access_mode = modes[access_mode].value
                    if isinstance(access_mode, Enum):
                        access_mode = access_mode.value
                    version.access_mode = access_mode
                    update_mode = version.update_mode
                    if isinstance(update_mode, int):
                        update_mode = modes[update_mode].value
                    if isinstance(update_mode, Enum):
                        update_mode = update_mode.value
                    version.update_mode = update_mode
                if not index % 10:
                    transaction.savepoint()
                    print(' + ', end='')
        print()
    finally:
        set_local_registry(registry)
