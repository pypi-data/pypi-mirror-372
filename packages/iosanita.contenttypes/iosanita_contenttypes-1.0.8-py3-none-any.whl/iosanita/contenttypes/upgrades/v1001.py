# -*- coding: utf-8 -*-

from . import logger
from iosanita.contenttypes.events.common import SUBFOLDERS_MAPPING
from plone import api


# from plone import api


def upgrade(setup_tool=None):
    """ """
    logger.info("Running upgrade (Python): Exclude from nav service folders")

    for portal_type, mapping in SUBFOLDERS_MAPPING.items():
        children_ids = [x["id"] for x in mapping["content"]]

        container_brains = api.content.find(portal_type=portal_type)
        tot = len(container_brains)
        logger.info(f"Fixing {tot} {portal_type}")
        for brain in container_brains:
            item = brain.getObject()
            for child in item.listFolderContents():
                if child.getId() in children_ids and child.portal_type in [
                    "Document",
                    "Folder",
                ]:
                    child.exclude_from_nav = True
                    child.reindexObject(idxs=["exclude_from_nav"])
