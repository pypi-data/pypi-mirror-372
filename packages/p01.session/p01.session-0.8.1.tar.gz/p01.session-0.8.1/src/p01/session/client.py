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
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import hmac
import logging
import random
import time
from builtins import object

import six
from six import ensure_str
from six import ensure_binary
from zope.interface import implementer

try:
    from hashlib import sha1
except ImportError:
    import sha as sha1

try:
    from email.utils import formatdate
except ImportError:
    from email.Utils import formatdate

import zope.interface
from zope.session.interfaces import IClientId
from zope.publisher.interfaces import IRequest
from zope.publisher.interfaces.http import IHTTPApplicationRequest
from zope.schema.fieldproperty import FieldProperty
from zope.session.http import MissingClientIdException
from zope.session.http import digestEncode

from p01.session import interfaces

__docformat__ = 'restructuredtext'

logger = logging.getLogger()


@implementer(IClientId)
class ClientId(str):
    """Client Id implementation."""
    zope.component.adapts(IRequest)

    def __new__(cls, cid):
        if isinstance(cid, six.text_type):
            return str.__new__(cls, cid)
        else:
            raise TypeError("cid must be a string or Unicode")


@implementer(interfaces.IMemcacheClientIdFactory)
class MemcacheClientIdFactory(object):
    """Client id adapter factory managing and using cookies."""

    namespace = FieldProperty(interfaces.IMemcacheClientIdFactory['namespace'])
    secret = FieldProperty(interfaces.IMemcacheClientIdFactory['secret'])
    lifetime = FieldProperty(interfaces.IMemcacheClientIdFactory['lifetime'])
    domain = FieldProperty(interfaces.IMemcacheClientIdFactory['domain'])
    secure = FieldProperty(interfaces.IMemcacheClientIdFactory['secure'])
    postOnly = FieldProperty(interfaces.IMemcacheClientIdFactory['postOnly'])
    httpOnly = FieldProperty(interfaces.IMemcacheClientIdFactory['httpOnly'])

    def __init__(self, namespace, secret, lifetime=None, domain=None,
        secure=False, postOnly=False, httpOnly=False):
        """Initialize a client id adapter.

        Note, this adapter must get initalized in a module and use the same
        attrs in each instance.

        Note, the lifetime must get changed to 0 (zero) for use an infinit
        expire time. This means such cookie will exist in a new browser after
        close the current browser. This is normaly not what you need for
        authentication cookies.
        """
        self.namespace = ensure_str(namespace)
        self.secret = secret
        self.lifetime = lifetime
        self.domain = domain
        self.secure = secure
        self.postOnly = postOnly
        self.httpOnly = httpOnly

    def __call__(self, request):
        """Adapting a request returns an IClientId instance."""
        return ClientId(self.getClientId(request))

    def getClientId(self, request):
        """
        get the client id from cookie or generate a new one.
        :return: str (ascii)
        """

        sid = self.getRequestId(request)
        if sid is None:
            if self.postOnly and not (request.method == 'POST'):
                raise MissingClientIdException
            else:
                sid = self.generateUniqueId()
                self.setRequestId(request, sid)
        elif self.lifetime:
            # If we have a finite cookie lifetime, then set the cookie
            # on each request to avoid losing it.
            self.setRequestId(request, sid)

        return sid

    def generateUniqueId(self):
        """
        Generate a new, random, unique id.
        :return: str (ascii, length 54)
        """
        # 20 random Bytes -> 27 Zeichen nach digestEncode
        try:
            import os
            rnd = os.urandom(20)
        except Exception:
            # very old fallback
            rnd = sha1(ensure_binary("%.20f%.20f" % (random.random(), time.time()))).digest()
        s = digestEncode(rnd)
        s_bytes = ensure_binary(s)
        mac = hmac.new(s_bytes, ensure_binary(self.secret), digestmod=sha1).digest()
        out = s + digestEncode(mac)
        return out.decode('ascii')


    def getRequestId(self, request):
        """
        Get the unique Id from the cookie.
        :return: str (ascii)
        """
        response_cookie = request.response.getCookie(self.namespace)
        if response_cookie:
            sid = response_cookie['value']
        else:
            request = IHTTPApplicationRequest(request)
            sid = request.getCookies().get(self.namespace, None)
        # If there is an id set on the response, use that but
        # don't trust it.  We need to check the response in case
        # there has already been a new session created during the
        # course of this request.
        if sid is None or len(sid) != 54:
            return None
        s, mac = sid[:27], sid[27:]

        # call encode() on value as a workaround a bug where the hmac
        # module only accepts str() types in Python 2.6

        # Generate the expected MAC using HMAC
        expected_mac = hmac.new(
            ensure_binary(s),  # ensure 's' is a byte string
            ensure_binary(self.secret),  # ensure 'self.secret' is a byte string
            digestmod=sha1
        ).digest()

        # Ensure expected_mac is in byte form, just in case digestEncode returns a str
        expected_mac = ensure_binary(digestEncode(expected_mac))

        # Ensure both mac and expected_mac are byte strings for comparison
        if ensure_binary(mac) != expected_mac:
            return None
        else:
            if isinstance(sid, bytes):
                return sid.decode()
            else:
                return sid

    def setRequestId(self, request, id):
        """ Set cookie with id on request. """
        response = request.response
        options = {}
        if self.lifetime is not None:
            if self.lifetime:
                expires = formatdate(time.time() + self.lifetime,
                                     localtime=False, usegmt=True)
            else:
                expires = 'Tue, 19 Jan 2038 00:00:00 GMT'  # Expire far in the future if lifetime is None
            options['expires'] = expires

        if self.secure:
            options['secure'] = True

        if self.httpOnly:
            options['httponly'] = True

        if self.domain:
            options['domain'] = self.domain

        options['path'] = request.getApplicationURL(path_only=True)
        response.setCookie(self.namespace, id, **options)

        response.setHeader('Cache-Control', 'no-cache="Set-Cookie,Set-Cookie2"')
        response.setHeader('Pragma', 'no-cache')
        response.setHeader('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT')


@implementer(interfaces.IThirdPartyClientIdFactory)
class ThirdPartyClientIdFactory(object):
    """Client id adapter factory using third party cookies."""

    namespace = FieldProperty(
        interfaces.IThirdPartyClientIdFactory['namespace'])

    def __init__(self, namespace=None):
        self.namespace = namespace

    def __call__(self, request):
        return ClientId(self.getClientId(request))

    def getClientId(self, request):
        """Get the client id."""
        sid = self.getRequestId(request)
        if sid is None:
            raise MissingClientIdException
        return sid

    def getRequestId(self, request):
        """
        Generate a unique Id based on third party cookies.
        :return: str (ascii)
        """
        response_cookie = request.response.getCookie(self.namespace)
        if response_cookie:
            sid = response_cookie['value']
        else:
            request = IHTTPApplicationRequest(request)
            sid = request.getCookies().get(self.namespace, None)
        if isinstance(sid, bytes):
            return sid.decode()
        else:
            return sid

    def generateUniqueId(self):
        """We are not responsible for generate a cookie id."""
        logger.warning('ThirdPartyClientIdFactory is using thirdparty cookies '
                       'ignoring generateUniqueId call')

    def setRequestId(self, request, id):
        """We are not responsible for set a cookie."""
        logger.warning('ThirdPartyClientIdFactory is using thirdparty cookies '
                       'ignoring setRequestId call')


#def notifyVirtualHostChanged(event):
#    """Adjust cookie paths when IVirtualHostRequest information changes."""
#    request = IHTTPRequest(event.request, None)
#    if event.request is None:
#        return
#    cid = interfaces.IClientId(self.request)
#    for name, adapter in component.getAdaptersFor(interfaces.IClientId):
#        # Third party ClientId Managers need no modification at all
#        if not adapter.thirdparty:
#            cookie = request.response.getCookie(adapter.namespace)
#            if cookie:
#                adapter.setRequestId(request, cookie['value'])
