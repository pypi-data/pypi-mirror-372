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
$Id: connector.py 5551 2025-07-20 00:19:46Z roger.ineichen $
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import socket
import time
from builtins import object

from errno import EINVAL
from errno import EISCONN

try:
    import umemcache
    ERRORS = (IOError, RuntimeError, umemcache.MemcachedError, socket.error)
except ImportError:
    ERRORS = ()


class UltraConnector(object):
    """Same as Connector but using ultramemcache client

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

    """
    def __init__(self, clientFactory, server, debug=0, timeout=4,
        retries=3, delay=2):
        self.clientFactory = clientFactory
        self.server = server
        self.debug = debug
        self.timeout = timeout
        self._client = None
        self._create_client()
        self.retries = retries
        self.delay = delay

    def _create_connector(self):
        self._client = self.clientFactory(self.server)

    def _create_client(self):
        reconnect = self._client is not None
        if reconnect:
            try:
                self._client.close()
            except Exception:
                pass

        self._create_connector()
        if reconnect:
            retries = 0
            delay = self.delay
            while retries < self.retries:
                try:
                    self._client.connect()
                except socket.error as exc:
                    if exc.errno == EISCONN:
                        return   # we're good
                    if exc.errno == EINVAL:
                        # we're doomed, retry
                        self._create_connector()

                    time.sleep(delay)
                    retries += 1

            raise exc

    def connect(self):
        if self._client is None:
            self._create_client()
        return self._client.connect()

    def set(self, bKey, data, lifetime, flags=0, **kwargs):
        return self._client.set(bKey, data, lifetime, flags, **kwargs)

    def get(self, bKey):
        # NOTE: we don't use the flag and we don't serialize. We do this in
        # in our client implementation and allow explicit ti skip serialization
        # This is usefull for our p01.session implementation
        response = self._client.get(bKey)
        if response is not None:
            val, flags = response
            if val:
                return val
        return None

    def delete(self, bKey, lifetime=0, **kwargs):
        return self._client.delete(bKey, lifetime, **kwargs)

    def flush_all(self, lifetime=0, **kwargs):
        return self._client.flush_all(lifetime, **kwargs)

    def get_stats(self):
        return self._client.stats()

    def close(self):
        if self._client is not None and self._client.is_connected():
            self._client.close()

    def disconnect(self):
        if self._client is not None and self._client.is_connected():
            self._client.disconnect()
        