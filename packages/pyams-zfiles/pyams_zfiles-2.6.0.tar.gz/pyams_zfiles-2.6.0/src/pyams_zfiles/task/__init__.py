# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

import sys

from pyramid.httpexceptions import HTTPNotFound, HTTPUnauthorized
from sqlalchemy.exc import ResourceClosedError, SQLAlchemyError
from sqlalchemy.sql import text
from zope.schema.fieldproperty import FieldProperty

from pyams_alchemy.engine import get_user_session
from pyams_scheduler.interfaces.task import TASK_STATUS_EMPTY, TASK_STATUS_FAIL, TASK_STATUS_OK
from pyams_scheduler.interfaces.task.pipeline import IPipelineOutput
from pyams_scheduler.task import Task
from pyams_scheduler.task.pipeline import BasePipelineOutput
from pyams_security.interfaces.names import INTERNAL_USER_ID
from pyams_utils.adapter import adapter_config
from pyams_utils.factory import factory_config
from pyams_utils.registry import query_utility
from pyams_utils.request import query_request
from pyams_zfiles.interfaces import IDocumentContainer
from pyams_zfiles.task.interfaces import ISourceApplicationCheckerTask

__docformat__ = 'restructuredtext'

from pyams_zfiles import _


@factory_config(ISourceApplicationCheckerTask)
class SourceApplicationCheckerTask(Task):
    """Source application checker task

    This task is used to check registered OIDs in a database source (table or views) with
    OIDs registered for this application in ZFiles contents.

    Except if run in "dry-run" mode, documents which are stored in ZFiles but which are not
    registered anymore in the source application can be deleted.

    Documents which are registered in source application database but which are not in ZFiles
    anymore are also listed in task run report.
    """

    label = _("ZFiles source application checker")
    icon_class = 'fas fa-file-archive'

    application_names = FieldProperty(ISourceApplicationCheckerTask['application_names'])
    sql_engine = FieldProperty(ISourceApplicationCheckerTask['sql_engine'])
    table_name = FieldProperty(ISourceApplicationCheckerTask['table_name'])
    field_name = FieldProperty(ISourceApplicationCheckerTask['field_name'])
    dry_run = FieldProperty(ISourceApplicationCheckerTask['dry_run'])
    verbose_output = FieldProperty(ISourceApplicationCheckerTask['verbose_output'])

    principal_id = INTERNAL_USER_ID
    is_zodb_task = True

    def run(self, report, **kwargs):
        """Run ZFiles source application checker"""
        session = get_user_session(self.sql_engine,
                                   join=False,
                                   twophase=False,
                                   use_zope_extension=False)
        try:
            try:
                container = query_utility(IDocumentContainer)
                if container is None:
                    raise LookupError("Can't find documents container")
                request = query_request()
                report.writeln('ZFiles application documents checker', prefix='### ', suffix='\n')
                if self.dry_run:
                    report.writeln("---")
                    report.writeln("**DRY RUN: NO DOCUMENT HAS BEEN INJURED DURING THIS OPERATION!**")
                    report.writeln("---", suffix='\n')
                # get application OIDs
                application_oids = set((
                    result.oid
                    for result in session.execute(text(f'select distinct {self.field_name} as oid '
                                                       f'from {self.table_name}'))
                ))
                report.writeln(f"- Source application OIDs: **{len(application_oids)}**")
                # get ZFiles OIDs
                report.writeln(f"- ZFiles applications: {', '.join(self.application_names)}")
                zfiles_oids = set((
                    document.oid
                    for document in container.find_documents({'application_name': self.application_names})
                ))
                report.writeln(f"- ZFiles documents OIDs: **{len(zfiles_oids)}**")
                # check missing OIDs
                zfiles_missing_oids = application_oids - zfiles_oids
                report.writeln(f"- ZFiles missing documents: **{len(zfiles_missing_oids)}**")
                if self.verbose_output:
                    for oid in sorted(zfiles_missing_oids):
                        report.writeln(f"    + {oid}")
                # check orphan OIDs
                zfiles_orphan_oids = zfiles_oids - application_oids
                report.writeln(f"- ZFiles orphan documents: **{len(zfiles_orphan_oids)}**")
                for oid in sorted(zfiles_orphan_oids):
                    if self.dry_run:
                        report.writeln(f"    + {oid}: TO BE DELETED")
                    else:
                        try:
                            container.delete_document(oid, request)
                            report.writeln(f"    + {oid}: DELETED")
                        except HTTPNotFound:
                            report.writeln(f"    + {oid}: NOT FOUND")
                        except HTTPUnauthorized:
                            report.writeln(f"    + {oid}: UNAUTHORIZED")
                        except Exception as exc:
                            report.writeln(f"    + {oid}: UNKNOWN ERROR: {exc}")
                report.writeln('\n')
                return TASK_STATUS_OK, {
                    'missing': list(zfiles_missing_oids),
                    'orphaned': list(zfiles_orphan_oids)
                }
            except ResourceClosedError:
                report.writeln("SQL query returned no result.", suffix='\n')
                return TASK_STATUS_EMPTY, None
        except SQLAlchemyError:
            report.writeln('**An SQL error occurred**', suffix='\n')
            report.write_exception(*sys.exc_info())
            return TASK_STATUS_FAIL, None
        finally:
            session.rollback()


@adapter_config(required=ISourceApplicationCheckerTask,
                provides=IPipelineOutput)
class SourceApplicationCheckerTaskPipelineOutput(BasePipelineOutput):
    """Source application checker task pipeline output"""
