###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Tests
$Id: tests.py 3934 2014-03-17 07:38:52Z roger.ineichen $
"""
from __future__ import absolute_import
from __future__ import print_function
__docformat__ = "reStructuredText"

import doctest
import re
import unittest
from zope.testing import renormalizing

checker = renormalizing.RENormalizing([
    (re.compile('\r\n'), '\n'),
    ])


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('checker.txt',
                             globs={'print_function': print_function,
                                    'absolute_import': absolute_import},
                             ),
        doctest.DocFileSuite('../README.txt',
                             optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                             globs={'print_function': print_function,
                                    'absolute_import': absolute_import},
                             checker=checker
                             ),
        doctest.DocFileSuite('zcml.txt',
                             optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                             checker=checker
                             ),
    ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
