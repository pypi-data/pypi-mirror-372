======
README
======

This package provides an utility that abstracts a client for memcached
servers see: http://www.danga.com/memcached.

  >>> from pprint import pprint
  >>> from p01.memcache.testing import getFakeBackend
  >>> from six import ensure_text


  >>> def decode_cache(d):
  ...     # Wir nehmen UTF-8 als Standard, fallback auf latin-1
  ...     def _decode(val):
  ...         if isinstance(val, bytes):
  ...             try:
  ...                 return val.decode('utf-8')
  ...             except UnicodeDecodeError:
  ...                 return val.decode('latin-1')
  ...         return val
  ...     return {_decode(k): (_decode(v[0]), v[1]) for k, v in d.items()}

This test uses our fake memcached server setup. See testing.txt for more
information:

  >>> try:
  ...     from hashlib import md5
  ... except ImportError:
  ...     from md5 import new as md5
  >>> from p01.memcache.client import MemcacheClient
  >>> client = MemcacheClient(pickleProtocol=0)
  >>> print([s.decode('utf-8') if isinstance(s, bytes) else s for s in client.servers])
  [...'127.0.0.1:11211']

  >>> client.lifetime
  3600

To store a new value in the cache we just need to set it. The set
method returns the generated memcached key for the cache key. If this key is
a string the plain key get used, if the key is an integer it get converted
to a string, if a persistent object get used, the _p_oid value get used.
Anything else is using a value pickle as key Such a key will get converted to
a md5 hexdigest as memcached key.

We can use the buildKey method for generate such keys:

  >>> print(client.buildKey('cache_key').decode('utf-8') if isinstance(client.buildKey('cache_key'), bytes) else client.buildKey('cache_key'))
  0a42907b589a309ad94f8874eacbc63f

Such a generated key get returned if we call set:

  >>> k = client.set('cache_key', 'cached value')
  >>> print(k.decode('utf-8') if isinstance(k, bytes) else k)
  0a42907b589a309ad94f8874eacbc63f

As you can see set will return the same key as buildKey will generate:

  >>> k == client.buildKey('cache_key')
  True

  >>> client.query('cache_key')
  'cached value'

If we no longer need the cached value we can invalidate it.

  >>> client.invalidate('cache_key')
  >>> client.query('cache_key') is None
  True

We have extended the original implementation on memcache.py for unicode.

  >>> key = client.set('cache_key', u'cached value ä')
  >>> client.query('cache_key') == u'cached value ä'
  True

We can invalidate the hole cache.

  >>> backend = getFakeBackend(client)
  >>> pprint(decode_cache(backend.cache))
  {...'0a42907b589a309ad94f8874eacbc63f': (...', 0)}

  >>> client.invalidateAll()
  >>> backend.cache
  {}

  >>> client.query('cache_key') is None
  True


build key
---------

Since memcache only accepts strings as key and short keys are better then long
keys, the client library class provides a method buildKey which will generate
a memcache key for us. If you like to use other rules for build a key, just
implement your own buildKey method.

A key will get converted to an md5 hexdigest and if a namespace is used,
the based key get prefixed with the namespace. Let's setup two memcache clients,
one with a namespace and one with an empty namspace:

  >>> nc = MemcacheClient(namespace='testing', pickleProtocol=0)

A simple string as key will get directly used as key and a namespace get used
as prefix:

  >>> ensure_text(client.buildKey('foo')) == md5(b'foo').hexdigest()
  True

  >>> client.namespace = 'n'
  >>> ensure_text(client.buildKey('foo')) == md5(b'nfoo').hexdigest()
  True

Unicode get converted to UTF-8:

  >>> client.namespace = None
  >>> ensure_text(client.buildKey(u'bar')) == md5(u'bar'.encode('UTF-8')).hexdigest()
  True

  >>> client.namespace = 'n'
  >>> ensure_text(client.buildKey(u'bar')) == md5(u'nbar'.encode('UTF-8')).hexdigest()
  True

An integer get converted to a string as base:

  >>> client.namespace = None
  >>> ensure_text(client.buildKey(123)) == md5(b'123').hexdigest()
  True

  >>> client.namespace = 'n'
  >>> ensure_text(client.buildKey(123)) == md5(b'n123').hexdigest()
  True

An persistent object uses the _p_oid id as key base:

  >>> class Object(object):
  ...     _p_oid = b'abc123'
  >>> obj = Object()

  >>> client.namespace = None
  >>> ensure_text(client.buildKey(obj)) == md5(obj._p_oid).hexdigest()
  True

  >>> client.namespace = 'n'
  >>> ensure_text(client.buildKey(obj)) == md5(b'n%s' % obj._p_oid).hexdigest()
  True

Anything else get pickled with object cPickle dump md5 hash as key:

  >>> import pickle
  >>> from p01.memcache.testing import Pickable
  >>> pickable = Pickable()

  >>> client.namespace = None
  >>> p = pickle.dumps(pickable, protocol=0)
  >>> ensure_text(client.buildKey(pickable)) == md5(p).hexdigest()
  True

  >>> client.namespace = 'n'
  >>> p = pickle.dumps(pickable, protocol=0)
  >>> ensure_text(client.buildKey(pickable)) == md5(b'n%s' % p).hexdigest()
  True

Set the namespace back to None:

  >>> client.namespace = None
  >>> client.namespace is None
  True


pickle protocol
===============

We can use a faster pickle method if we set the protocol to a higher value.
By default we use -1 which chooses the fastet pickle available from the
python version which runs this code. For compatibility reason we choose
the protocol=0 option which guarantees stable tests for different python
version. Note you can't store values in memcache daemon with one pickle
protocol version and read them form another version.

As you can see we will get a different value for the different pickle protocol:

  >>> client.invalidateAll()
  >>> backend = getFakeBackend(client)
  >>> backend.cache
  {}

  >>> k = client.set('foo', u'bar')
  >>> print(k.decode('utf-8') if isinstance(k, bytes) else k)
  acbd18db4cc2f85cedef654fccc4a4d8

  >>> backend = getFakeBackend(client)
  >>> p1 = backend.cache[b'acbd18db4cc2f85cedef654fccc4a4d8']
  >>> v1 = p1[0]
  >>> print(v1.decode('utf-8') if isinstance(v1, bytes) else v1)
  Vbar
  p0
  .

  >>> v2 = p1[1]
  >>> print(v2.decode('utf-8') if isinstance(v2, bytes) else v2)
  0

  >>> pc = MemcacheClient(pickleProtocol=1)
  >>> k = pc.set('foo', u'bar')
  >>> print(k.decode('utf-8') if isinstance(k, bytes) else k)
  acbd18db4cc2f85cedef654fccc4a4d8

  >>> backend = getFakeBackend(client)
  >>> v = backend.cache[k]

  >>> print(v[1])
  0

  >>> p1 != k
  True

  >>> print(client.query('foo'))
  bar

  >>> print(pc.query('foo'))
  bar

  >>> client.query('foo') == pc.query('foo')
  True


Namespaces
==========

The utility provides the facility to use namespaces for keys in order
to let multiple utilities share the same memcached servers. A default
namespace can be set on the utility which is then used for any get and
query methods.

  >>> util1 = MemcacheClient(pickleProtocol=0, namespace='1')
  >>> util2 = MemcacheClient(pickleProtocol=0, namespace='2')
  >>> k = util1.set(1, 1)
  >>> k = util2.set(2, 2)
  >>> util1.query(1)
  1
  >>> util1.query(2) is None
  True
  >>> util2.query(2)
  2
  >>> util2.query(1) is None
  True

Note that if invalidatAll is called then all namespaces are deleted.

  >>> util1.invalidateAll()
  >>> util1.query(1) is util2.query(2) is None
  True


Raw Data
========

The utility allways generates md5 hash keys in order to have short keys
and the data get pickled before stored in memache. If we like to store
simple data, we can use the raw argument. If used, the data get storaed as is:

If raw is used, the data must be a string.

  >>> client.set('a', u'value of a', raw=True)
  Traceback (most recent call last):
  ...
  ValueError:...

  >>> client.invalidateAll()
  >>> backend = getFakeBackend(client)
  >>> backend.cache
  {}

  >>> v = client.set(b'a', b'value of a', raw=True)
  >>> print(v.decode('utf-8') if isinstance(v, bytes) else v)
  0cc175b9c0f1b6a831c399e269772661

As you can see, our fake memcache stores a raw string as value:

  >>> backend = getFakeBackend(client)
  >>> v = backend.cache[b'0cc175b9c0f1b6a831c399e269772661'][0]
  >>> print(v.decode('utf-8') if isinstance(v, bytes) else v)
  value of a

Now we need can get the value with the raw key. Note also the value
was treated as a string, so we get a string back instead of a unicode.

  >>> v = client.query(b'a', raw=True)
  >>> print(v.decode('utf-8') if isinstance(v, bytes) else v)
  value of a


Statistics
==========

A memcached server can return statistic data. Our fake memcached server does
not implement this method yet:

  >>> client.getStatistics()
  'Testing Stats'


Invalidation Event
==================

Events can be used to create invalidations. The event handler invalidates in
registered memcached utilities.

  >>> from zope import event
  >>> from zope import component
  >>> from p01.memcache import interfaces
  >>> cacheOne = MemcacheClient(pickleProtocol=0, namespace='one')
  >>> component.provideUtility(cacheOne, interfaces.IMemcacheClient,
  ...     name='cacheOne')
  >>> v = cacheOne.set('key1', 'Value1')
  >>> print(v.decode('utf-8') if isinstance(v, bytes) else v)
  7d701cfc74a8bfe87fe6d448bf23c8f2

  >>> cacheOne.query('key1')
  'Value1'

  >>> from p01.memcache.event import invalidateCache
  >>> component.provideHandler(invalidateCache)

  >>> from p01.memcache.event import InvalidateCacheEvent
  >>> event.notify(InvalidateCacheEvent('key1'))
  >>> cacheOne.query('key1') is None
  True

With more than one memcache utility we can invalidate in all utilities. Note,
this test uses an additional memcache server our fake memcache client which
uses a simple dict for store the key/values:

  >>> cacheTwo = MemcacheClient(pickleProtocol=0, namespace='two')
  >>> component.provideUtility(cacheTwo, interfaces.IMemcacheClient, name='two')
  >>> key = cacheOne.set('key', 'v1')
  >>> key = cacheTwo.set('key', 'v2')
  >>> cacheOne.query('key')
  'v1'

  >>> cacheTwo.query('key')
  'v2'

  >>> event.notify(InvalidateCacheEvent('key'))
  >>> cacheOne.query('key') is None
  True

  >>> cacheTwo.query('key') is None
  True

Or we specify in which memcache we want to invalidate.

  >>> key = cacheOne.set('key', 'v1')
  >>> key = cacheTwo.set('key', 'v2')
  >>> cacheOne.query('key')
  'v1'
  >>> cacheTwo.query('key')
  'v2'
  >>> event.notify(InvalidateCacheEvent('key', cacheName='cacheOne'))
  >>> cacheOne.query('key') is None
  True
  >>> cacheTwo.query('key') is None
  False
