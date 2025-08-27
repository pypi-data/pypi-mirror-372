# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from zope.interface import implementer

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.group import GroupManager

from pyams_form.interfaces.form import IForm, IInnerTabForm
from pyams_form.subform import InnerAddForm, InnerEditForm
from pyams_layer.interfaces import IPyAMSLayer
from pyams_scheduler.interfaces import MANAGE_TASKS_PERMISSION
from pyams_scheduler.interfaces.folder import ITaskContainer
from pyams_scheduler.task.zmi import BaseTaskAddForm, BaseTaskEditForm
from pyams_scheduler.task.zmi.interfaces import ITaskInnerEditForm
from pyams_scheduler.zmi.interfaces import ITaskContainerTable
from pyams_skin.viewlet.menu import MenuItem
from pyams_utils.adapter import adapter_config
from pyams_viewlet.viewlet import viewlet_config
from pyams_zfiles.task import SourceApplicationCheckerTask
from pyams_zfiles.task.interfaces import ISourceApplicationCheckerTask, ISourceApplicationCheckerTaskInfo
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.viewlet import IContextAddingsViewletManager

__docformat__ = 'restructuredtext'

from pyams_zfiles import _


class ISourceApplicationCheckerTaskForm(IForm):
    """Source application checker task form marker interface"""


@implementer(ISourceApplicationCheckerTaskForm)
class SourceApplicationCheckerTaskFormInfo(GroupManager):
    """Source application checker task form"""
    
    title = _("Source application checker task settings")
    fields = Fields(ISourceApplicationCheckerTaskInfo)


@viewlet_config(name='add-source-application-checker-task.menu',
                context=ITaskContainer, layer=IAdminLayer, view=ITaskContainerTable,
                manager=IContextAddingsViewletManager, weight=200,
                permission=MANAGE_TASKS_PERMISSION)
class SourceApplicationCheckerTaskAddMenu(MenuItem):
    """Source application checker task add menu"""
    
    label = _("Add ZFiles source application checker task...")
    href = 'add-source-application-checker-task.html'
    modal_target = True


@ajax_form_config(name='add-source-application-checker-task.html',
                  context=ITaskContainer, layer=IPyAMSLayer,
                  permission=MANAGE_TASKS_PERMISSION)
class SourceApplicationCheckerTaskAddForm(BaseTaskAddForm):
    """Source application checker task add form"""
    
    modal_class = 'modal-xl'
    
    content_factory = ISourceApplicationCheckerTask
    content_label = SourceApplicationCheckerTask.label


@adapter_config(name='source-application-checker-task-info.form',
                required=(ITaskContainer, IAdminLayer, SourceApplicationCheckerTaskAddForm),
                provides=IInnerTabForm)
class SourceApplicationCheckerTaskAddFormInfo(SourceApplicationCheckerTaskFormInfo, InnerAddForm):
    """Source application checker task inner add form"""


@ajax_form_config(name='properties.html',
                  context=ISourceApplicationCheckerTask, layer=IPyAMSLayer,
                  permission=MANAGE_TASKS_PERMISSION)
class SourceApplicationCheckerTaskEditForm(BaseTaskEditForm):
    """Source application checker task edit form"""
    
    modal_class = 'modal-xl'


@adapter_config(name='source-application-checker-task-info.form',
                required=(ISourceApplicationCheckerTask, IAdminLayer, SourceApplicationCheckerTaskEditForm),
                provides=IInnerTabForm)
@implementer(ITaskInnerEditForm)
class SourceApplicationCheckerTaskEditFormInfo(SourceApplicationCheckerTaskFormInfo, InnerEditForm):
    """Source application checker task inner edit form"""
