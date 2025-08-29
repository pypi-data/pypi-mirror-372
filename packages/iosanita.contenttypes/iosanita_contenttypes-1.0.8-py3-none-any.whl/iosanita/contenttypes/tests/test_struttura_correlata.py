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


class TestStrutturaCorrelata(unittest.TestCase):
    """"""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        intids = getUtility(IIntIds)

        self.struttura1 = api.content.create(
            container=self.portal, type="Struttura", title="struttura 1"
        )
        self.struttura2 = api.content.create(
            container=self.portal, type="Struttura", title="struttura 2"
        )
        self.struttura_test = api.content.create(
            container=self.portal,
            type="Struttura",
            title="Test struttura",
        )
        self.servizio_test = api.content.create(
            container=self.portal,
            type="Servizio",
            title="Test servizio",
        )
        self.struttura_test.struttura_correlata = [
            RelationValue(intids.getId(self.struttura1))
        ]
        self.servizio_test.struttura_correlata = [
            RelationValue(intids.getId(self.struttura1)),
            RelationValue(intids.getId(self.struttura2)),
        ]
        notify(ObjectModifiedEvent(self.struttura_test))
        notify(ObjectModifiedEvent(self.servizio_test))

    def test_struttura_correlata_reference_in_struttura_is_in_catalog(self):
        """ """
        res = api.content.find(struttura_correlata_uid=self.struttura1.UID())

        self.assertEqual(len(res), 2)
        uids = [x.UID for x in res]
        self.assertIn(self.struttura_test.UID(), uids)

    def test_struttura_correlata_reference_in_servizio_is_in_catalog(self):
        """ """
        res = api.content.find(struttura_correlata_uid=self.struttura1.UID())

        self.assertEqual(len(res), 2)
        uids = [x.UID for x in res]
        self.assertIn(self.servizio_test.UID(), uids)

        res = api.content.find(struttura_correlata_uid=self.struttura2.UID())

        self.assertEqual(len(res), 1)
        self.assertEqual(self.servizio_test.UID(), res[0].UID)
