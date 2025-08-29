# -*- coding: utf-8 -*-
from iosanita.contenttypes.interfaces.come_fare_per import IComeFarePer
from plone.dexterity.content import Container
from zope.interface import implementer


@implementer(IComeFarePer)
class ComeFarePer(Container):
    """ """
