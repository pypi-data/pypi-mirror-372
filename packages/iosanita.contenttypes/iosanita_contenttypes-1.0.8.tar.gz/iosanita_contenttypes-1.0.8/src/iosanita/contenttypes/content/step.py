# -*- coding: utf-8 -*-
from iosanita.contenttypes.interfaces.step import IStep
from plone.dexterity.content import Container
from zope.interface import implementer


@implementer(IStep)
class Step(Container):
    """ """
