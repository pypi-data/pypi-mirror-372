# -*- coding: utf-8 -*-
from plone import api


def upgrade(setup_tool=None):
    """ """
    portal_types = api.portal.get_tool(name="portal_types")

    behaviors = portal_types["Plone Site"].behaviors
    if "kitconcept.seo" not in behaviors:
        behaviors = list(behaviors)
        behaviors.append("kitconcept.seo")
        portal_types["Plone Site"].behaviors = tuple(behaviors)
