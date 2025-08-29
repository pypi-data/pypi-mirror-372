# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from iosanita.contenttypes.testing import INTEGRATION_TESTING
from iosanita.contenttypes.testing import RESTAPI_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from Products.CMFPlone.interfaces import ISelectableConstrainTypes

import unittest


class TestEventSchema(unittest.TestCase):
    layer = RESTAPI_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.request["LANGUAGE"] = "it"

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_behaviors_enabled_for_event(self):
        portal_types = api.portal.get_tool(name="portal_types")
        self.assertEqual(
            portal_types["Event"].behaviors,
            (
                "plone.textindexer",
                "plone.eventbasic",
                "plone.eventrecurrence",
                "plone.dublincore",
                "plone.namefromtitle",
                "plone.allowdiscussion",
                "plone.excludefromnavigation",
                "plone.shortname",
                "plone.versioning",
                "plone.locking",
                "plone.constraintypes",
                "volto.preview_image",
                "plone.translatable",
                "kitconcept.seo",
                "iosanita.contenttypes.behavior.a_chi_si_rivolge",
                "collective.taxonomy.generated.a_chi_si_rivolge_tassonomia",
                "iosanita.contenttypes.behavior.ulteriori_informazioni",
                "iosanita.contenttypes.behavior.evento",
                "iosanita.contenttypes.behavior.dove",
                "iosanita.contenttypes.behavior.contatti",
                "iosanita.contenttypes.behavior.ulteriori_informazioni",
                "collective.taxonomy.generated.tipologia_evento",
                "collective.taxonomy.generated.parliamo_di",
            ),
        )

    def test_event_fieldsets(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Event").json()
        self.assertEqual(len(resp["fieldsets"]), 14)
        self.assertEqual(
            [x.get("id") for x in resp["fieldsets"]],
            [
                "default",
                "cosa_e",
                "partecipanti",
                "a_chi_si_rivolge",
                "dove",
                "costi",
                "contatti",
                "ulteriori_informazioni",
                "contenuti_collegati",
                "categorization",
                "dates",
                "ownership",
                "settings",
                "seo",
            ],
        )

    def test_event_required_fields(self):
        resp = self.api_session.get("@types/Event").json()
        self.assertEqual(
            sorted(resp["required"]),
            sorted(
                [
                    "costo",
                    "descrizione_estesa",
                    "end",
                    "pdc_correlato",
                    "start",
                    "tipologia_evento",
                    "title",
                ]
            ),
        )

    def test_event_fields_default_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Event").json()
        self.assertEqual(
            resp["fieldsets"][0]["fields"],
            [
                "title",
                "description",
                "start",
                "end",
                "whole_day",
                "open_end",
                "sync_uid",
                "recurrence",
                "preview_image",
                "preview_caption",
                "tipologia_evento",
                "parliamo_di",
            ],
        )

    def test_event_fields_cosa_e_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Event").json()
        self.assertEqual(resp["fieldsets"][1]["fields"], ["descrizione_estesa"])

    def test_event_fields_partecipanti_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Event").json()
        self.assertEqual(
            resp["fieldsets"][2]["fields"],
            ["persona_correlata", "parteciperanno"],
        )

    def test_event_fields_a_chi_si_rivolge_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Event").json()
        self.assertEqual(
            resp["fieldsets"][3]["fields"],
            ["a_chi_si_rivolge", "a_chi_si_rivolge_tassonomia"],
        )

    def test_event_fields_dove_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Event").json()
        self.assertEqual(
            resp["fieldsets"][4]["fields"],
            [
                "webinar",
                "struttura_correlata",
                "nome_sede",
                "street",
                "zip_code",
                "city",
                "provincia",
                "circoscrizione",
                "country",
                "geolocation",
            ],
        )

    def test_event_fields_costi_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Event").json()
        self.assertEqual(
            resp["fieldsets"][5]["fields"],
            ["costo"],
        )

    def test_event_fields_contatti_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Event").json()
        self.assertEqual(
            resp["fieldsets"][6]["fields"],
            [
                "pdc_correlato",
                "organizzato_da_interno",
                "organizzato_da_esterno",
                "patrocinato_da",
            ],
        )

    def test_event_fields_ulteriori_informazioni_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Event").json()
        self.assertEqual(resp["fieldsets"][7]["fields"], ["ulteriori_informazioni"])

    def test_event_fields_contenuti_collegati_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Event").json()
        self.assertEqual(resp["fieldsets"][8]["fields"], ["eventi_correlati"])


class TestEvent(unittest.TestCase):
    """"""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_if_event_has_children_events_is_indexed_as_rassegna(self):
        parent = api.content.create(container=self.portal, type="Event", title="parent")

        brain = api.content.find(UID=parent.UID())[0]

        self.assertFalse(brain.rassegna)

        api.content.create(container=parent, type="Event", title="child")

        brain = api.content.find(UID=parent.UID())[0]

        self.assertTrue(brain.rassegna)

    def test_event_default_children(self):
        event = api.content.create(container=self.portal, type="Event", title="xxx")

        self.assertEqual(
            event.keys(), ["immagini", "video", "sponsor-evento", "allegati"]
        )

    def test_event_immagini_has_filtered_addable_types(self):
        event = api.content.create(container=self.portal, type="Event", title="xxx")
        immagini = ISelectableConstrainTypes(event["immagini"])
        self.assertEqual(immagini.getConstrainTypesMode(), 1)
        self.assertEqual(immagini.getLocallyAllowedTypes(), ["Link", "Image"])

    def test_event_video_has_filtered_addable_types(self):
        event = api.content.create(container=self.portal, type="Event", title="xxx")
        video = ISelectableConstrainTypes(event["video"])
        self.assertEqual(video.getConstrainTypesMode(), 1)
        self.assertEqual(video.getLocallyAllowedTypes(), ["Link"])

    def test_event_sponsor_has_filtered_addable_types(self):
        event = api.content.create(container=self.portal, type="Event", title="xxx")
        sponsor = ISelectableConstrainTypes(event["sponsor-evento"])
        self.assertEqual(sponsor.getConstrainTypesMode(), 1)
        self.assertEqual(sponsor.getLocallyAllowedTypes(), ["Link"])

    def test_event_allegati_has_filtered_addable_types(self):
        event = api.content.create(container=self.portal, type="Event", title="xxx")
        allegati = ISelectableConstrainTypes(event["allegati"])
        self.assertEqual(allegati.getConstrainTypesMode(), 1)
        self.assertEqual(allegati.getLocallyAllowedTypes(), ["File"])
