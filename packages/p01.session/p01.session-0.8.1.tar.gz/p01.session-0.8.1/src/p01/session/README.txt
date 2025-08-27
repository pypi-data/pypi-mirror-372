===============
Session concept
===============

This package provides a different session handling concept.

Short summary

- offer simple session adapter

- intelligent session data management by session data manager

- built-in transaction management

- cached session data manager in request annotation 

- stores session data in memcache or similar key, value storage

- intelligent session data handling, update session data only if something
  changed

- use known session keys for authenticated users. This allow to invalidate
  session data for other known users (KnownSession)


Session
-------

This test does not expect a memcache server running. The test will use the 
fake memcache client defined in p01.memcache.testing.

  >>> from future import standard_library
  >>> standard_library.install_aliases()
  >>> from p01.memcache.testing import getFakeBackend

  >>> import zope.component
  >>> from p01.memcache import interfaces
  >>> from p01.memcache.testing import FakeMemcacheClient
  >>> client = FakeMemcacheClient()
  >>> zope.component.provideUtility(client, interfaces.IMemcacheClient, name='')
  >>> client.invalidateAll()

Setup a session adapter and a test request:

  >>> from zope.publisher.interfaces import IRequest
  >>> from p01.session import interfaces
  >>> from p01.session import session
  >>> from p01.session import testing

We also need to setup a participation (request):

  >>> from io import StringIO
  >>> from zope.publisher.http import HTTPRequest
  >>> request = HTTPRequest(StringIO(''), {})

And we need a IClientId Adapter:

  >>> from zope.publisher.interfaces import IRequest
  >>> from zope.session.interfaces import IClientId
  >>> from p01.session.client import MemcacheClientIdFactory
  >>> namespace = 'zope3_cs_123'
  >>> secret = 'very secure'
  >>> mcim = MemcacheClientIdFactory(namespace, secret)
  >>> zope.component.provideAdapter(mcim, (IRequest,), provides=IClientId)

The simplest way to use a session is to call the session with a request. As you
can see we will get the same session with the same session id:

  >>> session.Session(request)
  <Session ...>

If we register the session adapter, we can use them by adapting a request:

  >>> zope.component.provideAdapter(session.Session, (IRequest,),
  ...     interfaces.ISession)
  >>> s = interfaces.ISession(request)
  >>> s
  <Session ...>

We can now get data from the session.

  >>> data = s['mySessionDataKey'.encode()]
  >>> data
  {}
  >>> type(data)
  <class 'p01.session.session.SessionData'>

  >>> data['info'] = 'stored in fake memcache'
  >>> data
  {...'info': ...'stored in fake memcache'}

Because the MemcacheSession is transaction aware we need to commit the
transaction to store data in the memcache.

  >>> import transaction
  >>> transaction.commit()

Now read the session data from memcache. Normaly you can't do this because we
don't know the real key for the stored session data. But we can simply check
our fake memcache backend cache:

  >>> backend = getFakeBackend(client)
  >>> value, flag = list(backend.cache.values())[0]

Now, check if we can convert the data:

  >>> import pickle
  >>> data = pickle.loads(value)
  >>> data
  {...'info': ...'stored in fake memcache'}

As you can see we can get the key, value from the data:

  >>> print(data.get('info'))
  stored in fake memcache


KnownSession
------------

As you can see, the KnownSession uses the principal id as client id. Let's
setup our KnownSession adapter:

  >>> testing.startInteraction()
  >>> zope.component.provideAdapter(session.KnownSession, (IRequest,),
  ...     interfaces.ISession)

Use our fake request which provides a dummy principal setup:

  >>> principal = testing.Principal()
  >>> request = testing.Participation(principal)
  >>> interfaces.ISession(request)
  <KnownSession ...'roger.ineichen'>