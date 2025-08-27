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

from future import standard_library

standard_library.install_aliases()
from builtins import str
from builtins import object
import six
import pickle
import time
import logging
import transaction
import threading
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

import zope.interface
import zope.component
from zope.interface import implementer
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from zope.publisher.interfaces import IRequest
from zope.session.interfaces import IClientId

from p01.memcache.interfaces import IMemcacheClient
from p01.session import interfaces

log = logging.getLogger('p01.session')
TLOCAL = threading.local()

def ensure_bytes(value, encoding='utf-8'):
    if isinstance(value, six.text_type):
        return value.encode(encoding)
    return value

@implementer(interfaces.ISessionData)
class SessionData(dict):
    """See zope.app.session.interfaces.ISessionData"""
    timestamp = 0


@implementer(interfaces.ISessionDataManager)
class SessionDataManager(dict, object):
    """Session data manager which knows how to get session data from a
    session cache storage e.g. memcached.
    """

    def __init__(self, sessionName, client, cid, commitInterval, tm, transaction):
        self.transaction_manager = tm  # useless but defined by interface
        self.transaction = transaction
        self.sessionName = sessionName
        self.client = client
        self.commitInterval = commitInterval
        self.cid = cid
        self._origin = {}

    def abort(self, trans):
        pass

    def tpc_begin(self, trans):
        pass

    def commit(self, trans):
        pass

    def tpc_vote(self, trans):
        pass

    def tpc_finish(self, trans):
        # we commit here because this could never fail, see transaction
        self.dump()

    def tpc_abort(self, trans):
        pass

    def sortKey(self):
        return str(id(self))

    def __getitem__(self, key):
        if key in self:
            data = super(SessionDataManager, self).__getitem__(key)
        else:
            mKey = '%s.%s' % (self.cid, key)
            m = md5(ensure_bytes(mKey))
            raw = self.client.query(m.hexdigest(), raw=True)
            if raw is not None:
                data = pickle.loads(raw)
                self._origin[key] = raw
            else:
                data = SessionData()
                data.timestamp = time.time()
                raw = pickle.dumps(data, protocol=self.client.pickleProtocol)
                self._origin[key] = raw
            super(SessionDataManager, self).__setitem__(key, data)
        return data

    def dump(self):
        t = time.time()
        for key, data in list(self.items()):
            org = self._origin.get(key)
            nextTime = data.timestamp + self.commitInterval
            if org is None or (t > nextTime) or (org != pickle.dumps(data, protocol=self.client.pickleProtocol)):
                mKey = '%s.%s' % (self.cid, key)
                m = md5(ensure_bytes(mKey))
                data.timestamp = time.time()
                self.client.set(m.hexdigest(), data)

    def __repr__(self):
        return '<%s %r for %r>' % (self.__class__.__name__, self.sessionName, self.cid)


@implementer(interfaces.ISession)
class Session(object):
    """Session adapter implementation.

    The session data get stored in memcached or a similar storage.

    If you use a commitInterval number e.g. (60*5) 5 minutes, the session data
    get stored each 5 minutes. Note you should allways use a smaller
    commitInterval then the lifetime used in the memcache client.

    The commitInterval is used for refresh stored data because it will
    write the data back to the memcached server. This is usefull if the
    memcached server starts to remove data because of to less ram.
    """

    zope.component.adapts(IRequest)

    _client = None
    _cid = None
    cacheName = ''
    commitInterval = 60 * 5  # 5 minutes

    def __init__(self, request):
        self.request = request
        dm = request.annotations.get(self.sessionName)
        tm = transaction.manager
        txn = tm.get()
        if dm is None:
            dm = SessionDataManager(self.sessionName, self.client, self.cid,
                                    self.commitInterval, tm, txn)
            txn.join(dm)
            request.annotations[self.sessionName] = dm
        elif dm.transaction != txn:
            # if the dm in the request is there, this doesn't mean that the
            # transaction is still the same. Right now we rejoin the dm to the
            # new transaction.
            # rejoin after raise an exception which will start a new
            # transaction, see publication handleException
            txn.join(dm)
        self.context = dm

    @property
    def client(self):
        if self._client is None:
            self._client = zope.component.getUtility(IMemcacheClient, self.cacheName)
        return self._client

    @property
    def cid(self):
        if self._cid is None:
            self._cid = str(IClientId(self.request))
        return self._cid

    @property
    def sessionName(self):
        return self.__class__.__name__

    def get(self, key, default=None):
        # force to create a session
        return self[key]

    def __contains__(self, key):
        return key in self.context

    def __getitem__(self, key):
        return self.context[key]

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.cid)


@implementer(interfaces.IKnownSession)
class KnownSession(Session):
    """Session adapter implementation.

    A known session uses a known key for each users session which could get
    invalidated from another thread/process. This could be usefull if you need
    to implement a message system where a user will add messages for other
    users.

    Note: you need to make sure if a user get logged in and will get another
    client id that the session data get moved from the old key to the new one.
    Normaly this is done with an event subscriber for
    IAuthenticatedPrincipalCreated events if your IAuthentication concept
    supports such an event notification.

    This concept doesn't expose the real used key in the session storage
    e.g. memcached. We still use a md5 hash as key. See the dump method:

    mKey = '%s.%s' % (self.cid, key)
    m = md5(mKey)
    self.client.set(m.hexdigest(), data)

    """

    @property
    def cid(self):
        if self._cid is None:
            if IUnauthenticatedPrincipal.providedBy(self.request.principal):
                val = IClientId(self.request)
            else:
                val = self.request.principal.id
            self._cid = ensure_bytes(val).decode('utf-8')
        return self._cid
