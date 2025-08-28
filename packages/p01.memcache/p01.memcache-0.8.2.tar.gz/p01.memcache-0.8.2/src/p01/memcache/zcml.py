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

import zope.component.zcml
import zope.configuration.fields
import zope.interface
import zope.schema
import zope.security.zcml

from p01.memcache import client
from p01.memcache import interfaces


class IMemcacheDirective(zope.interface.Interface):
    """A directive to register a memcache client utility."""

    factory = zope.configuration.fields.GlobalObject(
        title=u"Memcache utility class",
        description=u"A class that provides a memcache utility",
        required=True,
        default=client.MemcacheClient)

    servers = zope.configuration.fields.Tokens(
        title=u"List of servers <hostname>:<port>",
        description=u"Servers defined as <hostname>:<port>",
        value_type=zope.schema.BytesLine(
            title=u"Server:Port",
            description=u"Server defined as <hostname>:<port>",
            missing_value='',
            required=True),
        required=True,
        default=['127.0.0.1:11211'])

    debug = zope.schema.Int(
        title=u"Debug flag 0 or 1",
        description=u"The debug flag 0 or 1",
        required=False,
        default=0)

    pickleProtocol = zope.schema.Int(
        title=u"Pickle protocol",
        description=u"The pickle protocol number 0, 1, 2 or -1 for latest",
        required=False,
        default=-1)

    lifetime = zope.schema.Int(
        title=u"Default Lifetime",
        description=u"The default lifetime of entries",
        required=True,
        default=3600,
        )

    namespace = zope.schema.ASCIILine(
        title=u"Default Namespace (ASCII)",
        description=u"The default namespace (ASCII) used by this client",
        required=False,
        default=None)

    name = zope.schema.TextLine(
        title=u"The name of the pagelet.",
        description=u"The name shows up in URLs/paths. For example 'foo'.",
        required=False,
        default=u'')

    permission = zope.security.zcml.Permission(
        title=u"Permission",
        description=u"Permission required to use this component.",
        required=False)


def memcache(_context, factory, name='', servers=['127.0.0.1:11211'],
    debug=0, pickleProtocol=-1, lifetime=None, namespace=None, permission=None):

    # setup and register utility
    provides = interfaces.IMemcacheClient
    component = factory(servers, debug, pickleProtocol, lifetime, namespace)
    zope.component.zcml.utility(_context, provides, component, permission, name)