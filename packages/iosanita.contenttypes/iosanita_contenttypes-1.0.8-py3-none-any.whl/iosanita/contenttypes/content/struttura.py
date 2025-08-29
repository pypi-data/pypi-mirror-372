# -*- coding: utf-8 -*-
from iosanita.contenttypes.interfaces.struttura import IStruttura
from plone.dexterity.content import Container
from zope.interface import implementer


@implementer(IStruttura)
class Struttura(Container):
    """ """
