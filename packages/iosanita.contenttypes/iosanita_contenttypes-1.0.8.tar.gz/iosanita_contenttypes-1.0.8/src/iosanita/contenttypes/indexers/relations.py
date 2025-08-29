# -*- coding: utf-8 -*-
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.decorator import indexer


@indexer(IDexterityContent)
def uo_correlata_uid(context, **kw):
    """ """
    return [
        x.to_object.UID()
        for x in getattr(context.aq_base, "uo_correlata", [])
        if x.to_object
    ]


@indexer(IDexterityContent)
def struttura_correlata_uid(context, **kw):
    """ """
    return [
        x.to_object.UID()
        for x in getattr(context.aq_base, "struttura_correlata", [])
        if x.to_object
    ]


@indexer(IDexterityContent)
def servizio_correlato_uid(context, **kw):
    """ """
    return [
        x.to_object.UID()
        for x in getattr(context.aq_base, "servizio_correlato", [])
        if x.to_object
    ]
