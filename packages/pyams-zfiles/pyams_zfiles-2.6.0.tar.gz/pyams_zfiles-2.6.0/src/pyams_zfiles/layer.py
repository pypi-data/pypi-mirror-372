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

"""PyAMS_zfiles.layer module

This modules defines custom PyAMS_zfiles layer and skin.
"""

from pyams_layer.interfaces import IPyAMSLayer, ISkin
from pyams_utils.registry import utility_config
from pyams_zfiles.interfaces import PYAMS_ZFILES_SKIN_NAME


__docformat__ = 'restructuredtext'

from pyams_zfiles import _


class IPyAMSZFilesLayer(IPyAMSLayer):
    """Custom ZFiles layer marker interface"""


@utility_config(name=PYAMS_ZFILES_SKIN_NAME, provides=ISkin)
class PyAMSZFilesSkin:
    """PyAMS ZFiles skin"""

    label = _("PyAMS ZFiles skin")
    layer = IPyAMSZFilesLayer
