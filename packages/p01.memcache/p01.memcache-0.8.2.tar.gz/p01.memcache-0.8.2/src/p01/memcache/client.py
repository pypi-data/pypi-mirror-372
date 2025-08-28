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
from __future__ import unicode_literals

from future import standard_library
standard_library.install_aliases()

from builtins import str
from builtins import object

import logging
import pickle
import six
import threading

try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

import pymemcache.client

import zope.interface
from zope.schema.fieldproperty import FieldProperty
from p01.memcache import interfaces


TLOCAL = threading.local()

log = logging.getLogger('p01.memcache')


@zope.interface.implementer(interfaces.IMemcacheClient)
class MemcacheClient(object):
    """Non persistent memcached client uasable as global utility.
    
    Note, this implementation uses thread local and works well with a threading
    concept like use in zope etc.

    If you use gevent the monkey path or the greenlet thread will die after
    it's live time. This will not be efficient since a gevent applicaiton can
    span over several greenlets and each greenlet will create a client.

    This means you should use the umemcache implementation which uses a
    connection pool which will handover open connections between threads
    or greenlets.
    """


    _memcacheClientFactory = pymemcache.client.HashClient

    servers = FieldProperty(interfaces.IMemcacheClient['servers'])
    debug = FieldProperty(interfaces.IMemcacheClient['debug'])
    namespace = FieldProperty(interfaces.IMemcacheClient['namespace'])
    lifetime = FieldProperty(interfaces.IMemcacheClient['lifetime'])
    pickleProtocol = FieldProperty(interfaces.IMemcacheClient['pickleProtocol'])

    def __init__(self, servers=['127.0.0.1:11211'], debug=0, pickleProtocol=-1,
        lifetime=None, namespace=None):
        self.servers = servers

        self.debug = debug
        self.pickleProtocol = pickleProtocol
        if lifetime is not None:
            self.lifetime = lifetime
        if namespace is not None:
            self.namespace = namespace

    def buildKey(self, key):
        """Builds a (md5) memcache key based on the given key

        - if the key is a string, the plain key get used as base

        - if the key is unicode, the key get converted to UTF-8 as base

        - if the key is an int, the key get converted to string as base

        - if key is a persistent object its _p_oid is used as base

        - anything else will get pickled (including unicode)
        
        Such a base key get converted to an md5 hexdigest if a namespace is
        used, the namespace is used as key prefix.

        """

        if isinstance(key, int):
            bKey = six.ensure_binary(str(key))  # int >> str >> bytes
        elif isinstance(key, (six.binary_type, six.text_type)):
            bKey = six.ensure_binary(key)
        elif getattr(key, '_p_oid', None):
            bKey = six.ensure_binary(key._p_oid)
        else:
            bKey = pickle.dumps(key, protocol=self.pickleProtocol)

        if self.namespace is not None:
            bNamespace = six.ensure_binary(self.namespace)
            bKey = bNamespace + bKey

        return six.ensure_binary(md5(bKey).hexdigest())

    def set(self, key, data, lifetime=None, raw=False):
        bKey = self.buildKey(key)
        if lifetime is None:
            lifetime = self.lifetime
        if raw:
            if not isinstance(data, six.binary_type):
                raise ValueError(
                    "Data must be bytes, %s given" % type(data).__name__, data)
        else:
            data = pickle.dumps(data, protocol=self.pickleProtocol)
        if self.debug:
            log.debug('set: %r -> %s, %r, %r, %r' % (key, bKey, len(data),
                self.namespace, lifetime))

        if self.client.set(bKey, data, lifetime):
            return bKey
        return None

    def query(self, key, raw=False, default=None):
        res = self.client.get(self.buildKey(key))
        if res is not None and self.debug:
            log.debug('query: %r, %r, %r, %r' % (key, len(res), self.namespace,
                raw))
        if res is None:
            return default
        if raw:
            return res
        return pickle.loads(res)

    def invalidate(self, key):
        log.debug('invalidate: %r, %r '% (key, self.namespace))
        self.client.delete(self.buildKey(key))

    def invalidateAll(self):
        self.client.flush_all()

    def getStatistics(self):
        return self.client.get_stats()

    @property
    def client(self):
        sKey = tuple(self.servers)
        mc = TLOCAL.__dict__.get(sKey, None)
        if mc is None:
            mc = self._memcacheClientFactory(self.servers, debug=self.debug,
                pickleProtocol=self.pickleProtocol)
            TLOCAL.__dict__[sKey] = mc
            servers = ', '.join(s.decode('utf-8') if isinstance(s, bytes) else s for s in self.servers)
            log.info('Creating new local memcache client for %s' % servers)
        return mc