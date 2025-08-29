# -*- coding: utf-8 -*-

from . import logger
from iosanita.contenttypes.events.common import SUBFOLDERS_MAPPING
from iosanita.contenttypes.utils import create_default_blocks
from plone import api
from Products.CMFPlone.interfaces import ISelectableConstrainTypes


def upgrade(setup_tool=None):
    """ """
    logger.info("Running upgrade (Python): Add allegati folder to ComeFarePer ct")

    portal_type = "ComeFarePer"
    mapping = SUBFOLDERS_MAPPING[portal_type]
    children_id = [x["id"] for x in mapping["content"]][0]

    container_brains = api.content.find(portal_type=portal_type)
    tot = len(container_brains)
    logger.info(f"Fixing {tot} {portal_type}")
    for brain in container_brains:
        item = brain.getObject()
        if children_id not in item.keys():
            ptype = mapping.get("type", "Document")
            child = api.content.create(
                container=item,
                type=ptype,
                title=mapping["content"][0]["title"],
                id=children_id,
            )

            create_default_blocks(context=child)

            child.exclude_from_search = True
            child.reindexObject(idxs=["exclude_from_search"])

            child.exclude_from_nav = True
            child.reindexObject(idxs=["exclude_from_nav"])

            if mapping["content"][0].get("allowed_types", ()):
                constraints_child = ISelectableConstrainTypes(child)
                constraints_child.setConstrainTypesMode(1)
                constraints_child.setLocallyAllowedTypes(
                    mapping["content"][0].get("allowed_types", ())
                )
