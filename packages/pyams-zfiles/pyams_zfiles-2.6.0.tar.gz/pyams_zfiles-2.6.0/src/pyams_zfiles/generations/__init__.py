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

"""PyAMS_zfiles.generations module

This module is checking for registered documents container utility and required
catalog indexes.
"""

import sys
from importlib import import_module

from zope.dublincore.interfaces import IZopeDublinCore

from pyams_catalog.generations import check_required_indexes
from pyams_catalog.index import DatetimeIndexWithInterface, FieldIndexWithInterface, \
    KeywordIndexWithInterface
from pyams_catalog.interfaces import DATE_RESOLUTION
from pyams_security.index import PrincipalsRoleIndex
from pyams_site.generations import check_required_utilities
from pyams_site.interfaces import ISiteGenerations
from pyams_utils.registry import utility_config
from pyams_workflow.interfaces import IWorkflowState
from pyams_zfiles.interfaces import DOCUMENT_CONTAINER_NAME, IDocumentContainer, \
    IDocumentVersion, ZFILES_CREATOR_ROLE, ZFILES_OWNER_ROLE


__docformat__ = 'restructuredtext'


REQUIRED_UTILITIES = (
    (IDocumentContainer, '', None, DOCUMENT_CONTAINER_NAME),
)

REQUIRED_INDEXES = (
    ('zfile_oid', FieldIndexWithInterface, {
        'interface': IDocumentVersion,
        'discriminator': 'oid'
    }),
    ('zfile_title', FieldIndexWithInterface, {
        'interface': IDocumentVersion,
        'discriminator': 'title'
    }),
    ('zfile_application', FieldIndexWithInterface, {
        'interface': IDocumentVersion,
        'discriminator': 'application_name'
    }),
    ('zfile_hash', FieldIndexWithInterface, {
        'interface': IDocumentVersion,
        'discriminator': 'hash'
    }),
    ('zfile_properties', KeywordIndexWithInterface, {
        'interface': IDocumentVersion,
        'discriminator': 'index_properties'
    }),
    ('zfile_tags', KeywordIndexWithInterface, {
        'interface': IDocumentVersion,
        'discriminator': 'tags'
    }),
    ('zfile_creator', PrincipalsRoleIndex, {
        'role_id': ZFILES_CREATOR_ROLE
    }),
    ('zfile_owner', PrincipalsRoleIndex, {
        'role_id': ZFILES_OWNER_ROLE
    }),
    ('zfile_updater', FieldIndexWithInterface, {
        'interface': IDocumentVersion,
        'discriminator': 'updater'
    }),
    ('workflow_version', FieldIndexWithInterface, {
        'interface': IWorkflowState,
        'discriminator': 'version_id'
    }),
    ('workflow_state', FieldIndexWithInterface, {
        'interface': IWorkflowState,
        'discriminator': 'state'
    }),
    ('workflow_date', DatetimeIndexWithInterface, {
        'interface': IWorkflowState,
        'discriminator': 'state_date',
        'resolution': DATE_RESOLUTION
    }),
    ('workflow_principal', FieldIndexWithInterface, {
        'interface': IWorkflowState,
        'discriminator': 'state_principal'
    }),
    ('created_date', DatetimeIndexWithInterface, {
        'interface': IZopeDublinCore,
        'discriminator': 'created',
        'resolution': DATE_RESOLUTION
    }),
    ('modified_date', DatetimeIndexWithInterface, {
        'interface': IZopeDublinCore,
        'discriminator': 'modified',
        'resolution': DATE_RESOLUTION
    })
)


@utility_config(name='PyAMS ZFiles', provides=ISiteGenerations)
class ZFilesGenerationsChecker:
    """ZFiles generations checker"""

    order = 70
    generation = 3

    def evolve(self, site, current=None):  # pylint: disable=unused-argument, no-self-use
        """Check for required utilities"""
        check_required_utilities(site, REQUIRED_UTILITIES)
        check_required_indexes(site, REQUIRED_INDEXES)
        if not current:
            current = 1
        for generation in range(current, self.generation):
            module_name = 'pyams_zfiles.generations.evolve{}'.format(generation)
            module = sys.modules.get(module_name)
            if module is None:
                module = import_module(module_name)
            module.evolve(site)
