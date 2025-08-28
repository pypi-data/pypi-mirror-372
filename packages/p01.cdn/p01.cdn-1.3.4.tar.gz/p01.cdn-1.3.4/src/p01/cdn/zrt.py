##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Templated Resource Processor

$Id: zrt.py 5609 2025-08-25 11:34:42Z roger.ineichen $
"""
from __future__ import absolute_import

__docformat__='restructuredtext'

import re
import zope.interface
import zope.component
from zope.interface import implementer
from zope.pagetemplate import engine

from p01.cdn import interfaces


################################################################################
#
# expressions

# <EXPR-TYPE>"<INPUT-EXPR>" <EXPR-TYPE>"<OUTPUT-EXPR>" <NUM>
NAME = r'[a-zA-Z0-9_-]*'
ARGS_REGEX = re.compile(r' *(%s)"([^"]*)" *(%s)"([^"]*)" *([0-9]*)' %(NAME, NAME))


class BaseExpression(object):

    def __init__(self, source, context, request):
        self.source = source
        self.context = context
        self.request = request


@zope.interface.implementer(interfaces.IZRTInputExpression)
class StringInputExpression(BaseExpression):
    """A simple string input expression"""

    def process(self, text, outputExpr, count=None):
        regex = re.compile(re.escape(self.source))
        return regex.subn(outputExpr.process(), text, count or 0)


@zope.interface.implementer(interfaces.IZRTOutputExpression)
class StringOutputExpression(BaseExpression):
    """A simple string input expression"""

    def process(self, **kw):
        # Ignore any keyword arguments, since this is static replacement
        return self.source


@zope.interface.implementer(interfaces.IZRTInputExpression)
class RegexInputExpression(BaseExpression):
    """A regex string input expression"""

    def process(self, text, outputExpr, count=None):
        regex = re.compile(self.source)
        return regex.subn(outputExpr.process(), text, count or 0)


@zope.interface.implementer(interfaces.IZRTOutputExpression)
class TALESOutputExpression(BaseExpression):
    """A simple string input expression"""

    def process(self, **kw):
        expr = engine.TrustedEngine.compile(self.source)
        kw.update({'context': self.context, 'request': self.request})
        econtext = engine.TrustedEngine.getContext(kw)
        return expr(econtext)


@zope.interface.implementer(interfaces.IZRTCommand)
class Replace(object):
    """A ZRT Command to replace sub-strings of the text"""

    inputExpressions = {
        '': StringInputExpression,
        'str': StringInputExpression,
        're': RegexInputExpression,
        }

    outputExpressions = {
        '': StringOutputExpression,
        'str': StringOutputExpression,
        'tal': TALESOutputExpression,
        }

    def __init__(self, args, start, end):
        self.start = start
        self.end = end
        self.processArguments(args)

    @property
    def isAvailable(self):
        return self.num is None or self.num > 0

    def processArguments(self, args):
        match = ARGS_REGEX.match(args)
        if match is None:
            raise interfaces.ArgumentError(args)

        self.itype, self.input, self.otype, self.output, self.num = match.groups()
        self.num = self.num and int(self.num) or None

        if self.itype not in self.inputExpressions:
            raise ValueError(self.itype)

        if self.otype not in self.outputExpressions:
            raise ValueError(self.otype)

    def process(self, text, context, request):
        iexpr = self.inputExpressions[self.itype](
            self.input, context, request)
        oexpr = self.outputExpressions[self.otype](
            self.output, context, request)
        text, num = iexpr.process(text, oexpr, self.num)
        if self.num is not None:
            self.num -= num
        return text


################################################################################
#
# cdn expressions

@implementer(interfaces.IZRTOutputExpression)
class CDNInputExpression(BaseExpression):
    """A simple string input expression"""

# XXX: probably RegexInputExpression is also broken
    def process(self, text, outputExpr, count=None):
        """Process simple string without backslash convertion

        Prevent backslash convertion, see re.sub documenations which says:
        any backslash escapes in it are processed. That is, \n is converted
        to a single newline character.
        This shold fix an issue with json2.js which has the following code:

        meta = {    // table of character substitutions
           '\b': '\\b',
           '\t': '\\t',
           '\n': '\\n',
           '\f': '\\f',
           '\r': '\\r',
           '"' : '\\"',
           '\\': '\\\\'
        },
        """
        regex = re.compile(re.escape(r'%s' % self.source))
        return regex.subn(r'%s' % outputExpr.process(), r'%s' % text, count or 0)


@implementer(interfaces.IZRTOutputExpression)
class CDNIncludeOutputExpression(BaseExpression):
    """CDN resource include expression"""

    def process(self, **kw):
        # Ignore any keyword arguments, since this is static replacement
        name = self.source
        resource = zope.component.queryAdapter(self.request, name=name)
        f = open(resource.path, 'rb')
        data = f.read()
        f.close()
        data = data.decode('utf-8', 'replace')
        # NOTE, this replaces the missing structure concept and prevents from
        # replace '\n' with '' and '\\n' with '\n' see json2.js as a sample
        return data.replace('\\', '\\\\')


@implementer(interfaces.IZRTCommand)
class CDNReplace(Replace):
    """ASame as Replace with additional cdn include expression

    You can use this additional expression as:

    /* zrt-replace:"REPLACE_THIS" include"RESOURCE_NAME" */
    REPLACE_THIS
    """

    inputExpressions = {
        '': CDNInputExpression,
        'str': CDNInputExpression,
        're': RegexInputExpression,
        }

    outputExpressions = {
        '': StringOutputExpression,
        'str': StringOutputExpression,
        'tal': TALESOutputExpression,
        'include': CDNIncludeOutputExpression,
        }
