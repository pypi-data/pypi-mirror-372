# -*- coding: utf-8 -*-

from . import logger
from plone import api


def upgrade(setup_tool=None):
    """ """
    logger.info(
        "Running upgrade (Python): Change behavior plone.basic => iosanita.basic"
    )

    portal_types = api.portal.get_tool(name="portal_types")

    for ptype in [
        "ComeFarePer",
        "Servizio",
        "Struttura",
        "UnitaOrganizzativa",
    ]:
        behaviors = []
        for behavior in portal_types[ptype].behaviors:
            if behavior == "plone.basic":
                behaviors.append("iosanita.basic")
            else:
                behaviors.append(behavior)
        portal_types[ptype].behaviors = tuple(behaviors)
