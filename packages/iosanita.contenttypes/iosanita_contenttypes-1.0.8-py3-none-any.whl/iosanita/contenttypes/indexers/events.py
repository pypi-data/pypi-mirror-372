# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import IEvent
from plone.indexer.decorator import indexer


@indexer(IEvent)
def event_location(context, **kw):
    """ """
    strutture_correlate = [x.to_object for x in context.strutture_correlate]
    strutture_correlate = filter(bool, strutture_correlate)
    strutture_correlate_title = [x.UID() for x in strutture_correlate]
    return strutture_correlate_title


@indexer(IEvent)
def rassegna(context, **kw):
    """ """
    children = context.values()
    return "Event" in [child.portal_type for child in children]
