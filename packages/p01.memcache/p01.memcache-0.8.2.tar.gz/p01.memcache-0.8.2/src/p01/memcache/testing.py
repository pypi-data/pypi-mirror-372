##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
$Id: memcache.py 77359 2007-07-03 15:54:09Z dobe $
"""
from __future__ import absolute_import

from builtins import object
from datetime import datetime
from datetime import timedelta
import six
try:
    unicode # p01.checker.silence
except NameError:
    unicode = str

import zope.component

from p01.memcache import interfaces

try:
    from p01.memcache import client
    has_memcache = True
except ImportError:
    has_memcache = False
try:
    from p01.memcache import uclient
    has_umemcache = True
except ImportError:
    has_umemcache = False



# shared fake memcache data storage, one per memcache client with different
# servers
HOSTS = [unicode('127.0.0.1:11211'),]
storage = {}
expires = {}

def getData(servers):
    servers = ''.join(s.decode('utf-8') if isinstance(s, bytes) else s for s in servers)
    return storage.setdefault(servers, {})

def getExpires(servers):
    servers = ''.join(s.decode('utf-8') if isinstance(s, bytes) else s for s in servers)
    return expires.setdefault(servers, {})

_marker = object()


class FakeMemcached(object):
    """Fake memcached server which makes sure to separate data."""

    def __init__(self, servers=HOSTS, debug=0, pickleProtocol=0,
        socket_timeout=4):
        self.servers = servers
        self.debug = debug
        self.pickleProtocol = pickleProtocol
        self.resetCounts()

    @property
    def cache(self):
        return getData(self.servers)

    @property
    def expires(self):
        return getExpires(self.servers)

    def connect(self):
        return 1

    def getStats(self):
        return []

    def set(self, key, data, lifetime=0, flags=0):
        # raise an error if not a string
        key = six.ensure_binary(key, encoding="ascii")
        data = six.ensure_binary(data, encoding="ascii")
        if lifetime:
            expires = datetime.now()+timedelta(seconds=lifetime)
        else:
            expires = _marker
        self.cache[key] = (data, flags)
        self.expires[key] = expires
        self._sets += 1
        return True

    def get(self, key):
        key = six.ensure_binary(key, encoding="ascii")
        data = self.cache.get(key, _marker)
        self._gets += 1
        if data is _marker:
            self._misses += 1
            return None

        expires = self.expires.get(key, _marker)
        if expires is _marker or datetime.now() < expires:
            self._hits += 1
            # python-memcache client returns single data
            return data[0]

        del self.cache[key]
        del self.expires[key]
        self._misses += 1
        return None

    def delete(self, key):
        if key in self.cache:
            del self.cache[key]
            del self.expires[key]

    def flush_all(self):
        global storage
        global expires
        import six
        storage[''.join(
            [six.text_type(s, 'utf-8') if isinstance(s, bytes) else s for s in self.servers]
        )] = {}
        # storage[''.join(self.servers)] = {}
        expires[''.join(
            [six.text_type(s, 'utf-8') if isinstance(s, bytes) else s for s in self.servers]
        )] = {}
        # expires[''.join(self.servers)] = {}

    def get_stats(self):
        return "Testing Stats"

    @property
    def gets(self):
        return self._gets

    @property
    def hits(self):
        return self._hits

    @property
    def misses(self):
        return self._misses

    @property
    def sets(self):
        return self._sets

    def resetCounts(self):
        self._hits = 0
        self._misses = 0
        self._gets = 0
        self._sets = 0


class FakeUltraMemcached(FakeMemcached):
    """Fake umemcache backend providing some different method signatures

    ultramemcache provides the following api. see:
    https://github.com/esnme/ultramemcache/blob/master/python/umemcache.cpp

    [X] def disconnect(self):
    [X] def is_connected(self):
    [X] def close(self):
    [X] def set(self, key, data, expiration = 0, flags = 0, async = False):
    [X] def add(self, key, data, expiration = 0, flags = 0, async = False):
    [X] def replace(self, key, data, expiration = 0, flags = 0, async = False):
    [X] def append(self, key, data, expiration = 0, flags = 0, async = False):
    [X] def prepend(self, key, data, expiration = 0, flags = 0, async = False):
    [X] def delete(self, key, expiration = 0, async = False):
    [x] def get(self, key, default = None):
    [X] def gets(self, key, default = None):
    [x] def get_multi(self, keys):
    [X] def gets_multi(self, keys):
    [X] def cas(self, key, data, cas_unique, expiration = 0, flags = 0, async = False):
    [X] def incr(self, key, increment, async = False):
    [X] def decr(self, key, increment, async = False):
    [X] def getr(self, key, default = None):
    
    [X] def version(self):
    [X] def stats(self):
    
    [X] def flush_all(self, expiration = 0, async = False):

    NOTE: The FakeUltraMemcached client only supports the relevant methods used
    by our UltraConnector.

    """

    def is_connected(self):
        return True

    def get(self, key):
        key = six.ensure_binary(key)
        data = self.cache.get(key, _marker)
        self._gets += 1
        if data is _marker:
            self._misses += 1
            return None

        expires = self.expires.get(key, _marker)
        if expires is _marker or datetime.now() < expires:
            self._hits += 1
            # ultramemcache library returns data, flag tuple
            return data

        del self.cache[key]
        del self.expires[key]
        self._misses += 1
        return None

    def set(self, key, data, expiration=0, flags=0, **kwargs):
        # raise an error if not a string
        key = six.ensure_binary(key)
        data = six.ensure_binary(data)
        if expiration:
            expires = datetime.now()+timedelta(seconds=expiration)
        else:
            expires = _marker
        self.cache[key] = (data, flags)
        self.expires[key] = expires
        self._sets += 1
        return True

    def delete(self, key, expiration=0, **kwargs):
        if key in self.cache:
            del self.cache[key]
            del self.expires[key]

    def flush_all(self, expiration=0, **kwargs):
        global storage
        global expires
        storage[''.join(self.servers)] = {}
        expires[''.join(self.servers)] = {}

    def stats(self):
        return "Testing Stats"

    def disconnect(self):
        pass

if has_memcache:
    class FakeMemcacheClient(client.MemcacheClient):
        """A memcache client which doesn't need a running memcache daemon.
        
        This fake client also shares the data accross threads.
        
        This fake MemcacheClient can be used if you need to setup an utility in 
        a test.
        """
    
        _memcacheClientFactory = FakeMemcached
        _client = None
    
        def __init__(self, servers=HOSTS, debug=0, pickleProtocol=-1,
            lifetime=None, namespace=None):
            super(FakeMemcacheClient, self).__init__(servers, debug,
                pickleProtocol, lifetime, namespace)
            # setup fake memcached server
            self._client = self._memcacheClientFactory(self.servers, self.debug,
                self.pickleProtocol)
    
        @property
        def client(self):
            return self._client
    
        @property
        def gets(self):
            return self.client.gets
    
        @property
        def hits(self):
            return self.client.hits
    
        @property
        def misses(self):
            return self.client.misses
    
        @property
        def sets(self):
            return self.client.sets
    
        def resetCounts(self):
            self.client.resetCounts()


if has_umemcache:
    class FakeUltraMemcacheClient(uclient.UltraMemcacheClient):
        """A memcache client which doesn't need a running memcache daemon.
        
        This fake client also shares the data accross threads.
        
        This fake MemcacheClient can be used if you need to setup an utility in 
        a test.
        """
    
        _memcacheClientFactory = FakeUltraMemcached
        _connector = None
        _client = None
    
        def __init__(self, servers=HOSTS, debug=0, pickleProtocol=-1,
            lifetime=3600, namespace=None, timeout=4):
            super(FakeUltraMemcacheClient, self).__init__(servers, debug,
                pickleProtocol, lifetime, namespace, timeout=timeout)
            # setup connector and client as singleton
            self._connector = self._getConnector()
            self._client = self._connector._client
    
        def _getConnector(self):
            if self._connector is None:
                self._connector = super(FakeUltraMemcacheClient, self)._getConnector()
            return self._connector
    
        @property
        def backend(self):
            return self._connector._client
    
        @property
        def gets(self):
            return self.backend.gets
    
        @property
        def hits(self):
            return self.backend.hits
    
        @property
        def misses(self):
            return self.backend.misses
    
        @property
        def sets(self):
            return self.backend.sets
    
        def resetCounts(self):
            self.backend.resetCounts()


def getFakeBackend(client):
    try:
        connector = client._getConnector()
        return connector._client
    except AttributeError:
        return client.client


class Pickable(object):
    """Pickable sample object used for testing"""

    title = u'Title'


_orgMemcacheClientFactory = None

def setUpFakeMemcached(test=None):
    """Patch all existing IMemcachClient utilities.
    
    This method can be used for patch all existing memcache clients at class
    level.
    """
    global _orgMemcacheClientFactory
    global storage
    global expires
    storage = {}
    expires = {}
    _orgMemcacheClientFactory = client.MemcacheClient._memcacheClientFactory
    client.MemcacheClient._memcacheClientFactory = FakeMemcached
    # setup fake client
    fClient = FakeMemcacheClient()
    zope.component.provideUtility(fClient, interfaces.IMemcacheClient, name='')
    fClient.invalidateAll()


def tearDownFakeMemcached(test=None):
    if _orgMemcacheClientFactory is not None:
        client.MemcacheClient._memcacheClientFactory = _orgMemcacheClientFactory
    global storage
    global expires
    storage = {}
    expires = {}


_orgUltraMemcacheClientFactory = None

def setUpFakeUltraMemcached(test=None):
    """Patch UltraMemcacheClient factory.
    
    This method can be used for patch all existing memcache clients at class
    level.
    """
    global _orgUltraMemcacheClientFactory
    global storage
    global expires
    storage = {}
    expires = {}
    _orgUltraMemcacheClientFactory = uclient.UltraMemcacheClient._memcacheClientFactory
    uclient.UltraMemcacheClient._memcacheClientFactory = FakeUltraMemcached
    # setup fake client
    fClient = FakeUltraMemcacheClient()
    zope.component.provideUtility(fClient, interfaces.IMemcacheClient, name='')
    fClient.invalidateAll()


def tearDownFakeUltraMemcached(test=None):
    if _orgUltraMemcacheClientFactory is not None:
        uclient.UltraMemcacheClient._memcacheClientFactory = _orgUltraMemcacheClientFactory
    global storage
    global expires
    storage = {}
    expires = {}