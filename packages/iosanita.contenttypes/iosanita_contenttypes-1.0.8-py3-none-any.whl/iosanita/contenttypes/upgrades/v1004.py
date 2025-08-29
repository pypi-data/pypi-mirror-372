# -*- coding: utf-8 -*-

from . import logger
from plone import api


def upgrade(setup_tool=None):
    """ """
    logger.info("Running upgrade (Python): Set dove fields required")

    portal_types = api.portal.get_tool(name="portal_types")

    for ptype in [
        "Struttura",
        "UnitaOrganizzativa",
    ]:
        behaviors = []
        for behavior in portal_types[ptype].behaviors:
            if behavior == "iosanita.contenttypes.behavior.dove":
                behaviors.append("iosanita.contenttypes.behavior.dove_required")
            else:
                behaviors.append(behavior)
        portal_types[ptype].behaviors = tuple(behaviors)

    # enable normale one for persona and event
    behaviors = list(portal_types["Persona"].behaviors)
    if "iosanita.contenttypes.behavior.dove" not in behaviors:
        behaviors.insert(
            behaviors.index("collective.taxonomy.generated.incarico") + 1,
            "iosanita.contenttypes.behavior.dove",
        )
        portal_types["Persona"].behaviors = tuple(behaviors)

    behaviors = list(portal_types["Event"].behaviors)
    if "iosanita.contenttypes.behavior.dove" not in behaviors:
        behaviors.insert(
            behaviors.index("iosanita.contenttypes.behavior.evento") + 1,
            "iosanita.contenttypes.behavior.dove",
        )
        portal_types["Event"].behaviors = tuple(behaviors)
