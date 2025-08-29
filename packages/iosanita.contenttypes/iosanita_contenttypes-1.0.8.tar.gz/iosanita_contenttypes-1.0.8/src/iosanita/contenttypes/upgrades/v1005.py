# -*- coding: utf-8 -*-

from . import logger
from plone import api
from plone.app.upgrade.utils import loadMigrationProfile


def upgrade(setup_tool=None):
    """ """
    logger.info("Running upgrade (Python): Add Subject_bando index")
    loadMigrationProfile(api.portal.get(), "iosanita.contenttypes.upgrades:1005")

    brains = api.content.find(portal_type="Bando")
    i = 0
    tot = len(brains)
    logger.info("### START CONVERSION FIELDS RICHTEXT -> DRAFTJS ###")
    for brain in brains:
        i += 1
        if i % 100 == 0:
            logger.info(f"Progress: {i}/{tot}")
        obj = brain.getObject()
        obj.reindexObject(idxs=["Subject_bando"])
