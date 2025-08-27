#
# Copyright (c) 2015-2022 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_zfiles.generations.evolve1 module

This module handles ZFiles migration to generation 2.
"""

__docformat__ = 'restructuredtext'

import logging
from zope.annotation import IAnnotations

from pyams_utils.factory import create_object
from pyams_utils.registry import get_local_registry, query_utility, set_local_registry
from pyams_zfiles.interfaces import DEFAULT_CONFIGURATION_NAME, DOCUMENT_SYNCHRONIZER_KEY, \
    IDocumentContainer, IDocumentSynchronizer, IDocumentSynchronizerConfiguration


LOGGER = logging.getLogger('PyAMS (ZFiles)')


def evolve(site):
    """Evolve 1: update roles annotations"""
    registry = get_local_registry()
    try:
        set_local_registry(site.getSiteManager())
        container = query_utility(IDocumentContainer)
        if container is not None:
            annotations = IAnnotations(container)
            synchronizer = annotations.get(DOCUMENT_SYNCHRONIZER_KEY)  # pylint: disable=assignment-from-no-return
            if synchronizer is not None:
                if not synchronizer.__name__:  # previous version
                    del annotations[DOCUMENT_SYNCHRONIZER_KEY]
                    new_synchronizer = IDocumentSynchronizer(container)
                    if getattr(synchronizer, 'target', None):
                        LOGGER.warning("Upgrading ZFiles documents container synchronizer")
                        configuration = create_object(IDocumentSynchronizerConfiguration)
                        if configuration is not None:
                            configuration.name = DEFAULT_CONFIGURATION_NAME
                            configuration.target = synchronizer.target
                            configuration.username = synchronizer.username
                            configuration.password = synchronizer.password
                            new_synchronizer[DEFAULT_CONFIGURATION_NAME] = configuration
                        del synchronizer.target
                        del synchronizer.username
                        del synchronizer.password
    finally:
        set_local_registry(registry)
