##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
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
from __future__ import absolute_import
from __future__ import print_function

import doctest
import unittest

import six
import z3c.testing

from p01.memcache import client
from p01.memcache import interfaces
from p01.memcache import testing

try:
    import umemcache
    hasUMemcache = True
except Exception:
    hasUMemcache = False


# from __future__ import unicode_literals


class MemcacheClientTest(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IMemcacheClient

    def getTestClass(self):
        return client.MemcacheClient


def test_suite():
    # default tests
    suites = (
        unittest.makeSuite(MemcacheClientTest),
        doctest.DocFileSuite('README.txt',
            globs={
                'print_function': print_function,
                # 'unicode_literals': unicode_literals,
                'absolute_import': absolute_import,
            },
            setUp=testing.setUpFakeMemcached,
            tearDown=testing.tearDownFakeMemcached,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        doctest.DocFileSuite('testing.txt',
            globs={
                'print_function': print_function,
                # 'unicode_literals': unicode_literals,
                'absolute_import': absolute_import,
            },
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
    )
    if hasUMemcache:
        # only available in python 2 and only with test-umemcache
        suites += ((
            doctest.DocFileSuite('ultramemcache.txt',
                globs={
                    'print_function': print_function,
                    # 'unicode_literals': unicode_literals,
                    'absolute_import': absolute_import,
                },
                setUp=testing.setUpFakeUltraMemcached,
                tearDown=testing.tearDownFakeUltraMemcached,
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
            ),
        ))
    # use level 2 tests (--all)
    suite = unittest.TestSuite((
        doctest.DocFileSuite('load-testing.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
    ))
    suite.level = 2
    suites += (suite,)
    return unittest.TestSuite(suites)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
