##############################################################################
#
# Copyright (c) 2013 Projekt01 GmbH and Contributors.
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
$Id: pool.py 5226 2025-04-12 19:24:32Z rodrigo.ristow $
"""
from __future__ import absolute_import

from future import standard_library

standard_library.install_aliases()
from builtins import range
from builtins import object

import sys
import time
import contextlib
import queue

# Sentinel used to mark an empty slot in the MCClientPool queue.
# Using sys.maxint as the timestamp ensures that empty slots will always
# sort *after* live connection objects in the queue.
EMPTY_SLOT = (sys.maxsize, None)


class ClientPool(object):
    """Client pool"""

    def __init__(self, factory, maxPoolSize=None, timeout=60, pooltime=None):
        self.factory = factory
        self.maxPoolSize = maxPoolSize
        self.timeout = timeout
        self.pooltime = pooltime
        self.pool = queue.PriorityQueue(maxPoolSize)
        # If there is a maxPoolSize, prime the queue with empty slots.
        if maxPoolSize is not None:
            for _ in range(maxPoolSize):
                self.pool.put(EMPTY_SLOT)

    @contextlib.contextmanager
    def reserve(self):
        """Context-manager to obtain a Client object from the pool."""
        ts, client = self._checkout_connection()
        try:
            yield client
        finally:
            self._checkin_connection(ts, client)

    def _checkout_connection(self):
        # If there's no maxPoolSize, no need to block waiting for a connection.
        blocking = self.maxPoolSize is not None
        # Loop until we get a non-stale connection, or we create a new one.
        while True:
            try:
                ts, client = self.pool.get(blocking, self.pooltime)
            except queue.Empty:
                if blocking:
                    #timeout
                    raise Exception("No connections available in the pool")
                else:
                    # No maxPoolSize and no free connections, create a new one.
                    # XXX TODO: we should be using a monotonic clock here.
                    now = int(time.time())
                    return now, self.factory()
            else:
                now = int(time.time())
                # If we got an empty slot placeholder, create a new connection.
                if client is None:
                    try:
                        return now, self.factory()
                    except Exception as e:
                        if self.maxPoolSize is not None:
                            # return slot to queue
                            self.pool.put(EMPTY_SLOT)
                        raise e
                # If the connection is not stale, go ahead and use it.
                if ts + self.timeout > now:
                    return ts, client
                # Otherwise, the connection is stale.
                # Close it, push an empty slot onto the queue, and retry.
                client.disconnect()
                self.pool.put(EMPTY_SLOT)
                continue

    def _checkin_connection(self, ts, client):
        """Return a connection to the pool."""
        # If the connection is now stale, don't return it to the pool.
        # Push an empty slot instead so that it will be refreshed when needed.
        now = int(time.time())
        if ts + self.timeout > now:
            self.pool.put((ts, client))
        else:
            if self.maxPoolSize is not None:
                self.pool.put(EMPTY_SLOT)