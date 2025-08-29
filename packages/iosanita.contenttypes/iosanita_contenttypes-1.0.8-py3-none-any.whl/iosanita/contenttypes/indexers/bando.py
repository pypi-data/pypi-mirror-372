# -*- coding: utf-8 -*-
from plone.indexer.decorator import indexer
from redturtle.bandi.interfaces import IBando


@indexer(IBando)
def Subject_bando(context, **kw):
    return context.Subject
