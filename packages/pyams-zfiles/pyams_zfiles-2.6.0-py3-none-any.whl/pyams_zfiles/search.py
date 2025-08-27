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

"""PyAMS_zfiles.search module

This module defines helper functions to search documents.
"""

import json
from datetime import date
from urllib.parse import parse_qsl

from dateutil import parser
from hypatia.query import All, Any, Comparator, Eq, Ge, Le

from pyams_catalog.query import and_, or_
from pyams_utils.date import date_to_datetime
from pyams_utils.interfaces.form import NO_VALUE_STRING
from pyams_utils.registry import get_utility
from pyams_utils.timezone import gmtime


__docformat__ = 'restructuredtext'

from pyams_zfiles.interfaces import ICatalogPropertiesIndexesContainer, IDocumentContainer

NULL_STRING = 'null'
LIST_SEPARATOR = ','


def get_list(value):
    """Check and convert the given value to a set, if required

    >>> from pyams_zfiles.search import get_list
    >>> get_list(None) is None
    True
    >>> get_list('') is None
    True
    >>> get_list('value1,value2')
    ['value1', 'value2']
    >>> get_list('value1, value2 ')
    ['value1', 'value2']
    """
    if value and isinstance(value, str):
        value = list(map(str.strip, value.split(LIST_SEPARATOR)))
    return value or None


def get_properties(value):
    """Check and convert given mapping value to a list of properties

    >>> from pprint import pprint
    >>> from pyams_zfiles.search import get_properties
    >>> get_properties(None) is None
    True
    >>> get_properties('') is None
    True
    >>> get_properties('value=1')
    {'value': {'1'}}
    >>> get_properties('value=1=3')
    {'value': {'1=3'}}
    >>> get_properties('{"value": 3}')
    {'value': {3}}
    >>> get_properties('value1=1&value2=2')
    {'value1': {'1'}, 'value2': {'2'}}
    >>> [(key, sorted(vals)) for key, vals in  get_properties('value1=1&value1=2&value2=2').items()]
    [('value1', ['1', '2']), ('value2', ['2'])]
    >>> get_properties({'value1': 1, 'value2': '2'})
    {'value1': {1}, 'value2': {'2'}}
    """
    if not value:
        return None
    result = {}
    if isinstance(value, str):
        # JSON encoded query
        if value.startswith('{'):
            value = json.loads(value)
            items = value.items()
        else:
            # URL encoded query
            items = parse_qsl(value)
    else:
        items = value.items()
    for key, val in items:
        result.setdefault(key, set()).add(val)
    return result


def get_version(value):
    """Check given version index

    >>> from pyams_zfiles.search import get_version
    >>> get_version(None) is None
    True
    >>> get_version(-1) is None
    True
    >>> get_version(1) == 1
    True
    """
    if value is not None:
        value = int(value)
    if value == -1:
        return None
    return value


def get_date(value):
    """Check and convert given value to a date, if required

    >>> from datetime import datetime
    >>> from pyams_zfiles.search import get_date
    >>> get_date(None) is None
    True
    >>> get_date('null') is None
    True
    >>> get_date(datetime(2021, 12, 3))
    datetime.datetime(2021, 12, 3, 0, 0, tzinfo=<UTC>)
    >>> get_date(datetime(2021, 12, 3).isoformat())
    datetime.datetime(2021, 12, 3, 0, 0, tzinfo=<UTC>)
    >>> get_date(datetime(2021, 12, 3, 12, 0, 0))
    datetime.datetime(2021, 12, 3, 12, 0, tzinfo=<UTC>)
    >>> get_date(datetime(2021, 12, 3, 12, 0, 0).isoformat())
    datetime.datetime(2021, 12, 3, 12, 0, tzinfo=<UTC>)
    """
    if value and isinstance(value, str):
        if value == NULL_STRING:
            return None
        value = parser.parse(value)
    if value:
        if isinstance(value, date):
            value = date_to_datetime(value)
        value = gmtime(value)
    return value or None


def get_range(value):
    """Convert given value to datetime range

    >>> from datetime import datetime
    >>> from pyams_zfiles.search import get_range
    >>> get_range((None, None))
    (None, None)
    >>> get_range((datetime(2021, 12, 3), None))
    (datetime.datetime(2021, 12, 3, 0, 0, tzinfo=<UTC>), None)
    >>> get_range('2021-12-03,null')
    (datetime.datetime(2021, 12, 3, 0, 0, tzinfo=<UTC>), None)
    >>> get_range((None, datetime(2021, 12, 3)))
    (None, datetime.datetime(2021, 12, 3, 0, 0, tzinfo=<UTC>))
    >>> get_range('null,2021-12-03')
    (None, datetime.datetime(2021, 12, 3, 0, 0, tzinfo=<UTC>))
    >>> get_range((datetime(2021, 12, 1), datetime(2021, 12, 3)))
    (datetime.datetime(2021, 12, 1, 0, 0, tzinfo=<UTC>),
     datetime.datetime(2021, 12, 3, 0, 0, tzinfo=<UTC>))
    >>> get_range('2021-12-01,2021-12-03')
    (datetime.datetime(2021, 12, 1, 0, 0, tzinfo=<UTC>),
     datetime.datetime(2021, 12, 3, 0, 0, tzinfo=<UTC>))
    """
    if isinstance(value, str):
        value = value.split(LIST_SEPARATOR)
    return tuple(map(get_date, value))


class InPropertiesList:
    """Check for list items

    Items are provided as a dict of sets, where dict keys are the names of searched properties
    and sets contains searched values; if a single property contains several values, these
    values are combined with an "or"; different properties are combined with an "and".
    """

    def __init__(self):
        container = get_utility(IDocumentContainer)
        self.index_names = ICatalogPropertiesIndexesContainer(container).index_names
        
    def __call__(self, params, catalog, index, value):
        for key, vals in value.items():
            queries = None
            for val in vals:
                if key in self.index_names:
                    index = f'zfile_property::{key}'
                    queries = or_(queries,
                                  Eq(catalog[index], val))
                else:
                    queries = or_(queries,
                                  Eq(catalog[index], f'{key}={val}'))
            params = and_(params, queries)
        return params


class Range:
    """Combine dates to create a ranged request"""

    def __call__(self, params, catalog, index, value):
        if not isinstance(value, (list, tuple)):
            return params
        after, before = value
        if after:
            params = and_(params,
                          Ge(catalog[index], after))
        if before:
            params = and_(params,
                          Le(catalog[index], before))
        return params


INDEX_ARGS = {
    'oid': (get_list, Any, 'zfile_oid'),
    'version': (get_version, Eq, 'workflow_version'),
    'title': (str.strip, Eq, 'zfile_title'),
    'application_name': (get_list, Eq, 'zfile_application'),
    'hash': (str.strip, Eq, 'zfile_hash'),
    'properties': (get_properties, InPropertiesList, 'zfile_properties'),
    'tags': (get_list, All, 'zfile_tags'),
    'status': (get_list, Any, 'workflow_state'),
    'creator': (get_list, Any, 'zfile_creator'),
    'created_date': (get_range, Range, 'created_date'),
    'owner': (get_list, Any, 'zfile_owner'),
    'updater': (get_list, Any, 'zfile_updater'),
    'updated_date': (get_range, Range, 'modified_date'),
    'status_updater': (get_list, Any, 'workflow_principal'),
    'status_update_date': (get_range, Range, 'workflow_date')
}


def make_query(catalog, params):
    """Make query from input parameters"""
    query = None
    for key, value in params.copy().items():
        if (value is None) or (value == {NO_VALUE_STRING}):
            params.pop(key)
        elif key not in INDEX_ARGS:
            params.setdefault('properties', {}).setdefault(key, params.pop(key))
    for key, value in params.items():
        args = INDEX_ARGS.get(key)
        if args is None:
            continue
        converter, operator, index = args
        if (value is not None) and (converter is not None):
            value = converter(value)
        if issubclass(operator, Comparator):
            if value is not None:
                query = and_(query, operator(catalog[index], value))  # pylint: disable=not-callable
        else:
            query = operator()(query, catalog, index, value)  # pylint: disable=not-callable
    return query
