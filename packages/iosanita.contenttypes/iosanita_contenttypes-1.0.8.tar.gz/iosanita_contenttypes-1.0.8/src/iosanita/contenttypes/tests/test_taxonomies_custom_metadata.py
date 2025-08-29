# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from iosanita.contenttypes.testing import INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class TestTaxonomiesCustomMetadata(unittest.TestCase):
    """"""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.request["LANGUAGE"] = "it"

        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_parliamo_di_metadata_has_array_of_objects(self):
        """ """
        struttura = api.content.create(
            container=self.portal,
            type="Struttura",
            title="Test servizio",
            parliamo_di=["ticket-ed-esenzioni", "igiene-pubblica"],
        )
        res = api.content.find(UID=struttura.UID())

        self.assertEqual(len(res), 1)
        self.assertEqual(
            res[0].parliamo_di, sorted(["ticket-ed-esenzioni", "igiene-pubblica"])
        )
        self.assertEqual(
            res[0].parliamo_di_metadata,
            [
                {"title": "Ticket ed esenzioni", "token": "ticket-ed-esenzioni"},
                {"title": "Igiene Pubblica", "token": "igiene-pubblica"},
            ],
        )

    def test_a_chi_si_rivolge_tassonomia_metadata_has_array_of_objects(self):
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
        res = api.content.find(UID=struttura.UID())

        self.assertEqual(len(res), 1)
        self.assertEqual(
            res[0].a_chi_si_rivolge_tassonomia,
            sorted(["farmacie", "imprese"]),
        )
        self.assertEqual(
            res[0].a_chi_si_rivolge_tassonomia_metadata,
            [
                {"title": "Farmacie", "token": "farmacie"},
                {"title": "Imprese", "token": "imprese"},
            ],
        )

    def test_incarico_has_last_taxonomy_leaf_value(self):
        """ """
        persona = api.content.create(
            container=self.portal,
            type="Persona",
            title="john doe",
            incarico=[
                "medico",
            ],
        )
        res = api.content.find(UID=persona.UID())[0]

        self.assertEqual(
            res.incarico_metadata,
            [{"title": "Medico", "token": "medico"}],
        )

    def test_tipologia_notizia_has_last_taxonomy_leaf_value(self):
        """ """
        news = api.content.create(
            container=self.portal,
            type="News Item",
            title="xxx",
            tipologia_notizia=[
                "comunicato-stampa",
            ],
        )
        res = api.content.find(UID=news.UID())[0]

        self.assertEqual(
            res.tipologia_notizia_metadata,
            [{"title": "Comunicato (stampa)", "token": "comunicato-stampa"}],
        )

    def test_tipologia_servizio_has_last_taxonomy_leaf_value(self):
        """ """
        servizio = api.content.create(
            container=self.portal,
            type="Servizio",
            title="xxx",
            tipologia_servizio=[
                "prevenzione-e-vaccini",
            ],
        )
        res = api.content.find(UID=servizio.UID())[0]

        self.assertEqual(
            res.tipologia_servizio_metadata,
            [{"title": "Prevenzione e vaccini", "token": "prevenzione-e-vaccini"}],
        )
