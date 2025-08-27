##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
$Id: zcml.py 75901 2007-05-23 02:58:48Z rogerineichen $
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import zope.component
import zope.configuration.fields
import zope.interface
import zope.schema
from zope.component.interface import provideInterface
from zope.publisher.interfaces import IRequest
from zope.session.interfaces import IClientId

from p01.session import client


class IClientIdAdapterDirective(zope.interface.Interface):
    """A directive to register a client id adapter.

    The pagelet directive also supports an undefined set of keyword arguments
    that are set as attributes on the pagelet after creation.
    """
    factory = zope.configuration.fields.GlobalObject(
        title=u"Client Id adapter factory",
        description=u"A class that provides a client id adapter factory",
        required=True,
        default=client.MemcacheClientIdFactory)

    layer = zope.configuration.fields.GlobalObject(
        title=u"Request type (layer)",
        description=u"The layer for which the IClientId adapter should be "
                    u"available",
        required=False,
        default=IRequest)

    namespace = zope.schema.ASCIILine(
        title=u"Cookie Name",
        description=u"Name of cookie used to maintain state. "
                    u"Must be unique to the site domain name, and only "
                    u"contain ASCII letters, digits and '_'",
        required=False,
        default=None)

    secret = zope.schema.TextLine(
        title=u"Secret",
        required=False,
        default=u'')

    lifetime = zope.schema.Int(
        title=u"Cookie Lifetime",
        description=u"Number of seconds until the browser expires the "
                    u"cookie. Leave blank expire the cookie when the "
                    u"browser is quit. Set to 0 to never expire.",
        min=0,
        required=False,
        default=None)

    domain = zope.schema.TextLine(
        title=u"Effective domain",
        description=u"An identification cookie can be restricted to a "
                    u"specific domain using this option. This option sets "
                    u"the ``domain`` attributefor the cookie header. It is "
                    u"useful for setting one identification cookie for "
                    u"multiple subdomains. So if this option is set to "
                    u"``.example.org``, the cookie will be available for "
                    u"subdomains like ``yourname.example.org``. "
                    u"Note that if you set this option to some domain, the "
                    u"identification cookie won't be available for other "
                    u"domains, so, for example you won't be able to login "
                    u"using the SessionCredentials plugin via another "
                    u"domain.",
        required=False,
        default=None)

    secure = zope.schema.Bool(
        title=u"Request Secure communication",
        required=False,
        default=False)

    postOnly = zope.schema.Bool(
        title=u"Only set cookie on POST requests",
        required=False,
        default=False)

    name = zope.schema.TextLine(
        title=u"The name of the pagelet.",
        description=u"The name shows up in URLs/paths. For example 'foo'.",
        required=False,
        default=u'')


def handler(methodName, *args, **kwargs):
    method = getattr(zope.component.getGlobalSiteManager(), methodName)
    method(*args, **kwargs)

def clientIdAdapter(_context, factory, layer, namespace, secret, lifetime=None,
        domain=None, secure=False, postOnly=False, name=''):

    if layer is None:
        if len(factory) == 1:
            layer = zope.component.adaptedBy(factory[0])

        if layer is None:
            raise TypeError("No for attribute was provided and can't "
                            "determine what the factory adapts.")

    factory = factory(namespace, secret, lifetime, domain, secure,
        postOnly)

    _context.action(
        discriminator = ('adapter', layer, IClientId, name),
        callable = handler,
        args = ('registerAdapter',
                factory, (layer,), IClientId, name, _context.info),
        )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = ('', IClientId))