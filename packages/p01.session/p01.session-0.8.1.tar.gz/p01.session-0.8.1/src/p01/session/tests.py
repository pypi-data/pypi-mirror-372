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
"""
$Id:$
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from future import standard_library

standard_library.install_aliases()
import unittest
from io import StringIO
from zope.publisher.http import HTTPRequest
import doctest
from doctest import DocFileSuite
from zope.session.interfaces import IClientId

import z3c.testing

from p01.session import interfaces
from p01.session import client
from p01.session import session
from p01.session import testing


class SessionTest(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ISession

    def getTestPos(self):
        request = HTTPRequest(StringIO(''), {})
        return (request,)

    def getTestClass(self):
        return session.Session


class KnownSessionTest(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IKnownSession

    def getTestPos(self):
        principal = testing.Principal()
        participation = testing.Participation(principal)
        return (participation,)

    def getTestClass(self):
        return session.KnownSession


class SessionDataTest(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ISessionData

    def getTestClass(self):
        return session.SessionData


class SessionDataManagerTest(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ISessionDataManager

    def getTestPos(self):
        return (None, None, None, None, None, None)

    def getTestClass(self):
        return session.SessionDataManager


class ClientIdTest(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return IClientId

    def getTestPos(self):
        return ('foo',)

    def getTestClass(self):
        return client.ClientId


class MemcacheClientIdFactoryTest(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IMemcacheClientIdFactory

    def getTestPos(self):
        return ('namespace', u'secret')

    def getTestClass(self):
        return client.MemcacheClientIdFactory


class ThirdPartyClientIdFactoryTest(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IThirdPartyClientIdFactory

    def getTestPos(self):
        return (u'namespace',)

    def getTestClass(self):
        return client.ThirdPartyClientIdFactory


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     globs={'print_function': print_function,
                            'unicode_literals': unicode_literals,
                            'absolute_import': absolute_import},
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        DocFileSuite('client.txt',
                     globs={'print_function': print_function,
                            'unicode_literals': unicode_literals,
                            'absolute_import': absolute_import},
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        unittest.makeSuite(SessionTest),
        unittest.makeSuite(KnownSessionTest),
        unittest.makeSuite(SessionDataTest),
        unittest.makeSuite(SessionDataManagerTest),
        unittest.makeSuite(ClientIdTest),
        unittest.makeSuite(MemcacheClientIdFactoryTest),
        unittest.makeSuite(ThirdPartyClientIdFactoryTest),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')