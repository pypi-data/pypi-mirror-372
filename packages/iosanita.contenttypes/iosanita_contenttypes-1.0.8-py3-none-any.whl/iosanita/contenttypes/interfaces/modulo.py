# -*- coding: utf-8 -*-
from iosanita.contenttypes.interfaces import IIosanitaContenttypes
from plone.supermodel import model


class IModulo(model.Schema, IIosanitaContenttypes):
    """Modulo"""
