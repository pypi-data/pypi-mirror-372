# -*- coding: utf-8 -*-
from iosanita.contenttypes.interfaces.documento import IDocumento
from plone.dexterity.content import Container
from zope.interface import implementer


@implementer(IDocumento)
class Documento(Container):
    """ """
