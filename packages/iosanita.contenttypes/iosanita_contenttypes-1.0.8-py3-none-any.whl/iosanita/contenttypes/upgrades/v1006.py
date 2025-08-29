# -*- coding: utf-8 -*-

from . import logger
from plone import api
from plone.app.upgrade.utils import installOrReinstallProduct


def upgrade(setup_tool=None):
    """ """
    logger.info("Install blocksfield")
    installOrReinstallProduct(api.portal.get(), "collective.volto.blocksfield")
