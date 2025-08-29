# -*- coding: utf-8 -*-
from iosanita.contenttypes.interfaces.modulo import IModulo
from plone.dexterity.content import Item
from zope.interface import implementer


@implementer(IModulo)
class Modulo(Item):
    """Modulo"""
