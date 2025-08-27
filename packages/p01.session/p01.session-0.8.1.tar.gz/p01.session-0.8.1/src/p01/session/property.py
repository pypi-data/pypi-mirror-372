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

import sys
from builtins import object

from zope.session.interfaces import ISession

_marker = object()


class SessionProperty(object):
    """Session property implementation.
    
    This session property can get used in persistent or non persistent objects.
    If we set values, they get stored in the session using the session key as
    name.
    """

    def __init__(self, field, sessionKey=None, name=None):
        if sessionKey is None:
            # calle is not initialized, the only info we have is the 
            # implementation advise, use the first interface as session key
            locals = sys._getframe(1).f_locals
            sessionKey = locals['__implements_advice_data__'][0][0].__identifier__
        self.sessionKey = sessionKey
        if name is None:
            name = field.__name__
        self.__field = field
        self.__name = name

    def __get__(self, inst, klass):
        if inst is None:
            return self
        session = ISession(inst.context)[self.sessionKey]
        value = session.get(self.__name, _marker)
        if value is _marker:
            field = self.__field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self.__name)
        return value

    def __set__(self, inst, value):
        field = self.__field.bind(inst)
        field.validate(value)
        session = ISession(inst.context)[self.sessionKey]
        if field.readonly and self.__name in session:
            raise ValueError(self.__name, 'field is readonly')
        session[self.__name] = value

    def __getattr__(self, name):
        return getattr(self.__field, name)