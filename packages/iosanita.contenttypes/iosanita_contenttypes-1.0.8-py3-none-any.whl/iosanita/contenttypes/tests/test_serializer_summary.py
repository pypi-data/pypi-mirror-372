# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from iosanita.contenttypes.testing import RESTAPI_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.testing import RelativeSession
from transaction import commit
from zope.component import getMultiAdapter

import unittest


class TestSerializerSummary(unittest.TestCase):
    """"""

    layer = RESTAPI_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.request["LANGUAGE"] = "it"

        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def test_summary_serializer_always_return_parliamo_di_metadata(self):
        """ """
        struttura = api.content.create(
            container=self.portal,
            type="Struttura",
            title="Test servizio",
            parliamo_di=["ticket-ed-esenzioni", "igiene-pubblica"],
        )
        commit()

        resp = self.api_session.get(f"@search?UID={struttura.UID()}").json()
        self.assertEqual(resp["items_total"], 1)
        self.assertIn("parliamo_di_metadata", resp["items"][0])
        self.assertEqual(
            resp["items"][0]["parliamo_di_metadata"],
            [
                {"title": "Ticket ed esenzioni", "token": "ticket-ed-esenzioni"},
                {"title": "Igiene Pubblica", "token": "igiene-pubblica"},
            ],
        )

    def test_summary_serializer_always_return_a_chi_si_rivolge_tassonomia_metadata(
        self,
    ):
        """ """
        struttura = api.content.create(
            container=self.portal,
            type="Struttura",
            title="Test servizio",
            a_chi_si_rivolge_tassonomia=[
                "farmacie",
                "imprese",
            ],
        )

        commit()
        resp = self.api_session.get(f"@search?UID={struttura.UID()}").json()

        self.assertEqual(resp["items_total"], 1)
        self.assertIn("a_chi_si_rivolge_tassonomia_metadata", resp["items"][0])
        self.assertEqual(
            resp["items"][0]["a_chi_si_rivolge_tassonomia_metadata"],
            [
                {"title": "Farmacie", "token": "farmacie"},
                {"title": "Imprese", "token": "imprese"},
            ],
        )

    def test_summary_serializer_always_return_id_metadata(
        self,
    ):
        """ """
        struttura = api.content.create(
            container=self.portal,
            type="Struttura",
            title="Test servizio",
            a_chi_si_rivolge_tassonomia=[
                "farmacie",
                "imprese",
            ],
        )

        commit()
        resp = self.api_session.get(f"@search?UID={struttura.UID()}").json()

        self.assertEqual(resp["items_total"], 1)
        self.assertIn("id", resp["items"][0])
        self.assertEqual(
            resp["items"][0]["id"],
            "test-servizio",
        )

    def test_summary_serializer_always_return_tipologia_notizia_metadata(
        self,
    ):
        """ """
        struttura = api.content.create(
            container=self.portal,
            type="Struttura",
            title="Test servizio",
            a_chi_si_rivolge_tassonomia=[
                "farmacie",
                "imprese",
            ],
        )

        news = api.content.create(
            container=self.portal,
            type="News Item",
            title="Test news",
            tipologia_notizia=["notizia"],
        )

        commit()
        resp = self.api_session.get(f"@search?UID={struttura.UID()}").json()

        self.assertEqual(resp["items_total"], 1)
        self.assertIn("tipologia_notizia", resp["items"][0])
        self.assertEqual(resp["items"][0]["tipologia_notizia"], [])

        resp = self.api_session.get(f"@search?UID={news.UID()}").json()

        self.assertEqual(resp["items_total"], 1)
        self.assertIn("tipologia_notizia", resp["items"][0])
        self.assertEqual(resp["items"][0]["tipologia_notizia"], ["notizia"])

    def test_summary_serializer_always_return_servizio_attivo_metadata(self):
        """ """
        servizio = api.content.create(
            container=self.portal,
            type="Servizio",
            title="Test",
        )
        commit()

        resp = self.api_session.get(f"@search?UID={servizio.UID()}").json()
        self.assertEqual(resp["items_total"], 1)
        self.assertIn("servizio_attivo", resp["items"][0])
        self.assertTrue(resp["items"][0]["servizio_attivo"])

        servizio.servizio_attivo = False
        servizio.reindexObject()
        commit()
        resp = self.api_session.get(f"@search?UID={servizio.UID()}").json()
        self.assertFalse(resp["items"][0]["servizio_attivo"])

    def test_summary_serializer_always_return_parent_metadata(self):
        """ """
        parent = api.content.create(
            container=self.portal,
            type="Document",
            title="Parent",
        )
        child = api.content.create(
            container=parent,
            type="Document",
            title="Child",
        )
        commit()

        resp = self.api_session.get(f"@search?UID={child.UID()}").json()
        self.assertIn("parent", resp["items"][0])
        self.assertEqual(resp["items"][0]["parent"]["title"], "Parent")
        self.assertEqual(resp["items"][0]["parent"]["UID"], parent.UID())

    def test_summary_serializer_return_has_children_info_in_GET_calls(self):
        """ """
        news = api.content.create(
            container=self.portal,
            type="News Item",
            title="Test news",
        )

        api.content.create(
            container=news["video"],
            type="Link",
            title="Test link",
        )
        commit()
        resp = self.api_session.get(news.absolute_url()).json()

        self.assertEqual(len(resp["items"]), 3)
        self.assertIn("has_children", resp["items"][0])
        self.assertIn("has_children", resp["items"][1])
        self.assertIn("has_children", resp["items"][2])
        self.assertFalse(resp["items"][0]["has_children"])
        self.assertTrue(resp["items"][1]["has_children"])
        self.assertFalse(resp["items"][2]["has_children"])

    def test_summary_serializer_does_not_return_has_children_info_in_POST_calls(self):
        """ """
        news = api.content.create(
            container=self.portal,
            type="News Item",
            title="Test news",
        )

        api.content.create(
            container=news["video"],
            type="Link",
            title="Test link",
        )
        commit()
        resp = self.api_session.post(
            "@querystring-search",
            json={
                "query": [
                    {
                        "i": "path",
                        "o": "plone.app.querystring.operation.string.absolutePath",
                        "v": f"{news['video'].UID()}::0",
                    }
                ]
            },
        ).json()
        self.assertEqual(len(resp["items"]), 1)
        self.assertNotIn("has_children", resp["items"][0])

        resp = self.api_session.post(
            "@querystring-search",
            json={
                "query": [
                    {
                        "i": "path",
                        "o": "plone.app.querystring.operation.string.absolutePath",
                        "v": f"{news['allegati'].UID()}::0",
                    }
                ]
            },
        ).json()

        self.assertEqual(len(resp["items"]), 1)
        self.assertNotIn("has_children", resp["items"][0])

    def test_pdc_summary_returns_also_contatti_data(self):
        contatti = [{"descrizione": "xxx", "tipo": "email", "valore": "foo@bar.it"}]

        pdc = api.content.create(
            container=self.portal,
            type="PuntoDiContatto",
            title="pdc",
            contatti=contatti,
        )

        serializer = getMultiAdapter((pdc, self.request), ISerializeToJsonSummary)()

        self.assertIn("contatti", serializer)
        self.assertEqual(serializer["contatti"], contatti)

    def test_summary_returns_bando_state_for_bandi_if_required_in_metadata_field(self):
        bando = api.content.create(container=self.portal, type="Bando", title="bando")

        serializer = getMultiAdapter((bando, self.request), ISerializeToJsonSummary)()

        self.assertNotIn("bando_state", serializer)

        self.request.form["metadata_fields"] = "bando_state"
        serializer = getMultiAdapter((bando, self.request), ISerializeToJsonSummary)()

        self.assertIn("bando_state", serializer)
