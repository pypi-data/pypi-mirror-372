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

"""PyAMS_zfiles.zmi.properties module

This module defines a custom widget to display properties.
"""

from pyams_form.browser.multi import MultiWidget
from pyams_form.interfaces import DISPLAY_MODE
from pyams_form.interfaces.widget import IMultiWidget
from pyams_form.template import widget_template_config
from pyams_form.widget import FieldWidget
from pyams_layer.interfaces import IFormLayer


__docformat__ = 'restructuredtext'


class IPropertiesWidget(IMultiWidget):
    """Properties widget interface"""


@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/properties-display.pt', layer=IFormLayer)
class PropertiesWidget(MultiWidget):
    """Properties widget"""


def PropertiesFieldWidget(field, request):  # pylint: disable=invalid-name
    """Properties field widget factory"""
    return FieldWidget(field, PropertiesWidget(request))
