##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
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
"""Resource NotFound exception page

$Id:$
"""
from __future__ import absolute_import
__docformat__ = "reStructuredText"

from zope.publisher.browser import BrowserPage


class ResourceNotFoundPage(BrowserPage):
    """Resource NotFound page"""

    def __call__(self):
        """Return no content since this renders a not found resource"""
        self.request.response.setStatus(404)
        return u""
