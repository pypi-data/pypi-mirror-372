# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from iosanita.contenttypes.testing import INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent

import unittest


class TestUOCorrelata(unittest.TestCase):
    """"""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.uo = api.content.create(
            container=self.portal, type="UnitaOrganizzativa", title="uo"
        )

    def test_uo_correlata_reference_is_in_catalog(self):
        """ """
        struttura = api.content.create(
            container=self.portal,
            type="Struttura",
            title="Test servizio",
        )
        intids = getUtility(IIntIds)
        struttura.uo_correlata = [RelationValue(intids.getId(self.uo))]
        notify(ObjectModifiedEvent(struttura))

        res = api.content.find(uo_correlata_uid=self.uo.UID())

        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].UID, struttura.UID())
