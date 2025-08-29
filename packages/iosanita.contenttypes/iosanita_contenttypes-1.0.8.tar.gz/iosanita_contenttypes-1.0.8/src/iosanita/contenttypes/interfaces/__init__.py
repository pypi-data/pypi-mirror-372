# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from redturtle.volto.interfaces import IRedturtleVoltoLayer
from zope.interface import Interface


class IIosanitaContenttypesLayer(IRedturtleVoltoLayer):
    """Marker interface that defines a browser layer."""


class IIosanitaContenttypes(Interface):
    """
    Marker interface
    """


class IoSanitaMigrationMarker(Interface):
    """
    Marker interface to disable validation checks and events during migration.
    """


class IoSanitaViewExtraData(Interface):
    """
    Marker interface to get the back references of a given object.
    """
