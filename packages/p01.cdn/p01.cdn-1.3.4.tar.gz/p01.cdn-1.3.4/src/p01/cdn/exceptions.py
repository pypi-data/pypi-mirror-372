##############################################################################
#
# Copyright (c) 2015 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
from __future__ import absolute_import
from zope.interface import implementer
__docformat__ = "reStructuredText"

import zope.interface

from p01.cdn import interfaces


@implementer(interfaces.IResourceNotFound)
class ResourceNotFound(Exception):
    """NotFound error for resources

    NOTE: this NotFound allows to register a custom NotFound page whcih is
    able to render a 500 status without to invoke the default NotFound page
    including the html layout.
    """

