# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from zope.interface import Interface
from zope.schema import Bool, Choice, List, TextLine

from pyams_alchemy.interfaces import ALCHEMY_ENGINES_VOCABULARY
from pyams_scheduler.interfaces import ITask
from pyams_zfiles.interfaces import PYAMS_ZFILES_APPLICATIONS_VOCABULARY

__docformat__ = 'restructuredtext'

from pyams_zfiles import _


class ISourceApplicationCheckerTaskInfo(Interface):
    """Source application checker task info"""

    application_names = List(title=_("Application names"),
                             description=_("Name of the source application"),
                             value_type=Choice(vocabulary=PYAMS_ZFILES_APPLICATIONS_VOCABULARY),
                             required=True)

    sql_engine = Choice(title=_("SQL engine"),
                        description=_("Name of the registered SQL engine used to "
                                      "extract documents OIDs"),
                        vocabulary=ALCHEMY_ENGINES_VOCABULARY,
                        required=True)

    table_name = TextLine(title=_("Table name"),
                          description=_("Name of the table or view containing documents "
                                        "OIDs"),
                          required=True,
                          default='V_GED')

    field_name = TextLine(title=_("Field name"),
                          description=_("Name of table field containing documents OIDs"),
                          required=True,
                          default='OID')

    dry_run = Bool(title=_("Dry run"),
                   description=_("If 'no', documents missing from source table will be "
                                 "deleted; otherwise, their OID will only be returned in "
                                 "task execution log"),
                   required=True,
                   default=True)

    verbose_output = Bool(title=_("Verbose output?"),
                          description=_("If 'Yes', task execution logs will be filled with "
                                        "more verbose output"),
                          required=True,
                          default=False)


class ISourceApplicationCheckerTask(ITask, ISourceApplicationCheckerTaskInfo):
    """Source application checker task interface"""
