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

from builtins import object

import zope.component
import zope.interface
from zope.interface import implementer

from p01.memcache import interfaces


@implementer(interfaces.IInvalidateCacheEvent)
class InvalidateCacheEvent(object):

    def __init__(self, key, cacheName=None):
        """Key argument could be an object if the object is used as key."""
        self.key = key
        self.cacheName = cacheName


@zope.component.adapter(interfaces.IInvalidateCacheEvent)
def invalidateCache(event):
    if event.cacheName is not None:
        cache = zope.component.queryUtility(interfaces.IMemcacheClient,
            event.cacheName)
        caches = []
        if cache is not None:
            caches.append(cache)
    else:
        caches = zope.component.getAllUtilitiesRegisteredFor(
            interfaces.IMemcacheClient)

    for cache in caches:
        cache.invalidate(event.key)
