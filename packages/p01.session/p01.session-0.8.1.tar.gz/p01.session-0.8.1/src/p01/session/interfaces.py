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
from __future__ import unicode_literals

import re

import zope.interface
import zope.schema
import zope.session.interfaces
from transaction.interfaces import IDataManager
from zope.interface.common.mapping import IReadMapping, IWriteMapping


class ISession(zope.session.interfaces.ISession):
    """Session interface."""

    client = zope.schema.Field(u"""Cache client""")

    cid = zope.schema.TextLine(
        title=u"client id",
        readonly=True)

    cacheName = zope.schema.TextLine(
        title=u"Cache utility name",
        default=u'')

    commitInterval = zope.schema.Int(
        title=u"Commit intervall",
        description=u"Update data after the intervall amout of seconds.",
        default=60*5)


class IKnownSession(ISession):
    """Session with principal id as client id."""


class ISessionDataManager(IDataManager):
    """Session data manager."""
    
    def __getitem__(key):
        """Returns session data."""


class ISessionData(IReadMapping, IWriteMapping):
    """Session data."""

    timestamp = zope.schema.Time(
        title=u"Data timestamp",
        description=u"Time the data was created or updated",
        required=True)


class IMemcacheClientIdFactory(zope.interface.Interface):
    """Client id manager managing and using cookies."""

    namespace = zope.schema.ASCIILine(
        title=u"Cookie Name",
        description=u"Name of cookie used to maintain state. "
                    u"Must be unique to the site domain name, and only "
                    u"contain ASCII letters, digits and '_'",
        required=True,
        min_length=1,
        max_length=30,
        constraint=re.compile("^[\d\w_]+$").search)

    lifetime = zope.schema.Int(
        title=u"Cookie Lifetime",
        description=u"Number of seconds until the browser expires the "
                    u"cookie. Leave blank expire the cookie when the "
                    u"browser is quit. Set to 0 to never expire.",
        min=0,
        required=False,
        default=None,
        missing_value=None)

    domain = zope.schema.TextLine(
        title=u"Effective domain",
        description=u"An identification cookie can be restricted to a "
                    u"specific domain using this option. This option sets "
                    u"the ``domain`` attribute for the cookie header. It is "
                    u"useful for setting one identification cookie for "
                    u"multiple subdomains. So if this option is set to "
                    u"``.example.org``, the cookie will be available for "
                    u"subdomains like ``yourname.example.org``. "
                    u"Note that if you set this option to some domain, the "
                    u"identification cookie won't be available for other "
                    u"domains, so, for example you won't be able to login "
                    u"using the SessionCredentials plugin via another "
                    u"domain.",
        required=False)

    secure = zope.schema.Bool(
        title=u"Request Secure communication",
        required=False,
        default=False)

    secret = zope.schema.TextLine(
        title=u"Secret",
        required=False,
        default=u'')

    postOnly = zope.schema.Bool(
        title=u"Only set cookie on POST requests",
        description=u"Only usefull if you don't have unauthenticated "
                    u"principals. Most time you need a clientId for a session "
                    u"and if the session is used for unauthenticated users you "
                    u"will need the clientId.",
        required=False,
        default=False)

    httpOnly = zope.schema.Bool(
        title=u"Cookie cannot be accessed through client side scripts",
        required=False,
        default=False,
        )


class IThirdPartyClientIdFactory(zope.interface.Interface):
    """Client id manager using only thirdparty cookies.

    Servers like Apache or Nginx have capabilities to issue identification
    cookies. If third party cookies are beeing used, Zope will never send a
    cookie back, just check for them. You only have to make sure that this
    client id manager and the server are using the same cookie namspace.

    """

    namespace = zope.schema.TextLine(
        title=u"Cookie Name",
        description=u"Name of cookie used to maintain state. "
                    u"Must be unique to the site domain name, and only "
                    u"contain ASCII letters, digits and '_'",
        required=True,
        min_length=1,
        max_length=30,
        constraint=re.compile("^[\d\w_]+$").search)