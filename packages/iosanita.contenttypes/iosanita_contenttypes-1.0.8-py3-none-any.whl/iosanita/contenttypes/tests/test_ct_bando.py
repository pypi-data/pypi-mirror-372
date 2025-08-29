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


class TestBandoSchema(unittest.TestCase):
    layer = RESTAPI_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_behaviors_enabled_for_bando(self):
        portal_types = api.portal.get_tool(name="portal_types")
        self.assertEqual(
            portal_types["Bando"].behaviors,
            (
                "plone.app.content.interfaces.INameFromTitle",
                "plone.app.dexterity.behaviors.discussion.IAllowDiscussion",
                "plone.app.dexterity.behaviors.exclfromnav.IExcludeFromNavigation",
                "plone.app.dexterity.behaviors.id.IShortName",
                "plone.app.dexterity.behaviors.metadata.IDublinCore",
                "plone.app.relationfield.behavior.IRelatedItems",
                "plone.app.versioningbehavior.behaviors.IVersionable",
                "plone.app.contenttypes.behaviors.tableofcontents.ITableOfContents",
                "plone.app.lockingbehavior.behaviors.ILocking",
                "Products.CMFPlone.interfaces.constrains.ISelectableConstrainTypes",
                "plone.versioning",
                "plone.translatable",
                "kitconcept.seo",
                "volto.preview_image",
                "iosanita.contenttypes.behavior.bando",
                "iosanita.contenttypes.behavior.a_chi_si_rivolge",
                "collective.taxonomy.generated.a_chi_si_rivolge_tassonomia",
                "collective.taxonomy.generated.parliamo_di",
            ),
        )

    def test_bando_fieldsets(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Bando").json()
        self.assertEqual(len(resp["fieldsets"]), 10)
        self.assertEqual(
            [x.get("id") for x in resp["fieldsets"]],
            [
                "default",
                "cosa_e",
                "a_chi_si_rivolge",
                "come_partecipare",
                "modalita_selezione",
                "settings",
                "categorization",
                "dates",
                "ownership",
                "seo",
            ],
        )

    def test_bando_required_fields(self):
        resp = self.api_session.get("@types/Bando").json()
        self.assertEqual(
            sorted(resp["required"]),
            sorted(
                [
                    "title",
                    "destinatari",
                    "tipologia_bando",
                    "descrizione_estesa",
                    "come_partecipare",
                    "modalita_selezione",
                ]
            ),
        )

    def test_bando_fields_default_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Bando").json()
        self.assertEqual(
            resp["fieldsets"][0]["fields"],
            [
                "title",
                "description",
                "riferimenti_bando",
                "apertura_bando",
                "scadenza_domande_bando",
                "chiusura_procedimento_bando",
                "scadenza_bando",
                "ente_bando",
                "destinatari",
                "tipologia_bando",
                "preview_image",
                "preview_caption",
                "note_aggiornamento",
                "parliamo_di",
            ],
        )

    def test_bando_fields_cosa_e_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Bando").json()
        self.assertEqual(resp["fieldsets"][1]["fields"], ["descrizione_estesa"])

    def test_bando_fields_a_chi_si_rivolge_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Bando").json()
        self.assertEqual(
            resp["fieldsets"][2]["fields"],
            ["a_chi_si_rivolge", "a_chi_si_rivolge_tassonomia"],
        )

    def test_bando_fields_come_partecipare_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Bando").json()
        self.assertEqual(
            resp["fieldsets"][3]["fields"],
            [
                "come_partecipare",
            ],
        )

    def test_bando_fields_modalita_selezione_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Bando").json()
        self.assertEqual(
            resp["fieldsets"][4]["fields"],
            [
                "modalita_selezione",
            ],
        )


class TestBando(unittest.TestCase):
    """"""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_bando_default_children(self):
        bando = api.content.create(container=self.portal, type="Bando", title="xxx")

        self.assertEqual(
            bando.keys(),
            ["graduatoria", "altri-allegati", "adempimenti-consequenziali"],
        )

        self.assertEqual("Bando Folder Deepening", bando.graduatoria.portal_type)
        self.assertEqual("Bando Folder Deepening", bando["altri-allegati"].portal_type)
        self.assertEqual(
            "Bando Folder Deepening", bando["adempimenti-consequenziali"].portal_type
        )

    def test_bando_graduatoria_has_no_filtered_addable_types(self):
        bando = api.content.create(container=self.portal, type="Bando", title="xxx")
        graduatoria = ISelectableConstrainTypes(bando["graduatoria"])
        self.assertEqual(graduatoria.getConstrainTypesMode(), 0)

    def test_bando_altri_allegati_has_no_filtered_addable_types(self):
        bando = api.content.create(container=self.portal, type="Bando", title="xxx")
        allegati = ISelectableConstrainTypes(bando["altri-allegati"])
        self.assertEqual(allegati.getConstrainTypesMode(), 0)

    def test_bando_adempimenti_has_no_filtered_addable_types(self):
        bando = api.content.create(container=self.portal, type="Bando", title="xxx")
        adempimenti = ISelectableConstrainTypes(bando["adempimenti-consequenziali"])
        self.assertEqual(adempimenti.getConstrainTypesMode(), 0)
