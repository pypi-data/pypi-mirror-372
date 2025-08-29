# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from iosanita.contenttypes.testing import INTEGRATION_TESTING
from iosanita.contenttypes.testing import RESTAPI_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.restapi.testing import RelativeSession
from Products.CMFPlone.interfaces import ISelectableConstrainTypes

import unittest


class TestPersonaSchema(unittest.TestCase):
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

    def test_behaviors_enabled_for_persona(self):
        portal_types = api.portal.get_tool(name="portal_types")
        self.assertEqual(
            portal_types["Persona"].behaviors,
            (
                "plone.namefromtitle",
                "plone.allowdiscussion",
                "plone.excludefromnavigation",
                "plone.shortname",
                "plone.ownership",
                "plone.publication",
                "plone.relateditems",
                "plone.categorization",
                "plone.locking",
                "plone.textindexer",
                "plone.translatable",
                "kitconcept.seo",
                "plone.versioning",
                "plone.constraintypes",
                "collective.taxonomy.generated.incarico",
                "iosanita.contenttypes.behavior.dove",
                "iosanita.contenttypes.behavior.contatti",
                "iosanita.contenttypes.behavior.ulteriori_informazioni",
            ),
        )

    def test_persona_fieldsets(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Persona").json()
        self.assertEqual(len(resp["fieldsets"]), 13)
        self.assertEqual(
            [x.get("id") for x in resp["fieldsets"]],
            [
                "default",
                "incarichi",
                "competenze",
                "dove",
                "orari_ricevimento",
                "contatti",
                "biografia",
                "ulteriori_informazioni",
                "settings",
                "ownership",
                "dates",
                "categorization",
                "seo",
            ],
        )

    def test_persona_required_fields(self):
        resp = self.api_session.get("@types/Persona").json()
        self.assertEqual(
            sorted(resp["required"]),
            sorted(
                [
                    "nome",
                    "cognome",
                    "incarico",
                    "competenze",
                    "pdc_correlato",
                ]
            ),
        )

    def test_persona_fields_default_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Persona").json()
        self.assertEqual(
            resp["fieldsets"][0]["fields"],
            [
                "cognome",
                "nome",
                "titolo_persona",
                "description",
                "image",
            ],
        )

    def test_persona_fields_incarichi_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Persona").json()
        self.assertEqual(
            resp["fieldsets"][1]["fields"], ["incarico", "altri_incarichi"]
        )

    def test_persona_fields_competenze_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Persona").json()
        self.assertEqual(
            resp["fieldsets"][2]["fields"],
            ["competenze"],
        )

    def test_persona_fields_dove_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Persona").json()
        self.assertEqual(
            resp["fieldsets"][3]["fields"],
            [
                "struttura_ricevimento",
                "struttura_in_cui_opera",
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

    def test_persona_fields_orari_ricevimento_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Persona").json()
        self.assertEqual(
            resp["fieldsets"][4]["fields"],
            ["orari_ricevimento"],
        )

    def test_persona_fields_contatti_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Persona").json()
        self.assertEqual(resp["fieldsets"][5]["fields"], ["pdc_correlato"])

    def test_persona_fields_biografia_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Persona").json()
        self.assertEqual(resp["fieldsets"][6]["fields"], ["biografia"])

    def test_persona_fields_ulteriori_informazioni_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Persona").json()
        self.assertEqual(resp["fieldsets"][7]["fields"], ["ulteriori_informazioni"])


class TestPersona(unittest.TestCase):
    """"""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_persona_title_composed(self):
        createContentInContainer(self.portal, "Persona", nome="John", cognome="Doe")
        self.assertIn("doe-john", self.portal.keys())
        persona = self.portal["doe-john"]
        self.assertEqual(persona.title, "Doe John")

    def test_persona_title_composed_also_with_titolo(self):
        createContentInContainer(
            self.portal, "Persona", nome="John", cognome="Doe", titolo_persona="dr."
        )
        self.assertIn("dr-doe-john", self.portal.keys())
        persona = self.portal["dr-doe-john"]
        self.assertEqual(persona.title, "dr. Doe John")

    def test_persona_default_children(self):
        createContentInContainer(
            self.portal, "Persona", nome="John", cognome="Doe", titolo_persona="dr."
        )
        persona = self.portal["dr-doe-john"]

        self.assertEqual(
            persona.keys(), ["curriculum-vitae", "immagini", "video", "allegati"]
        )

    def test_persona_immagini_has_filtered_addable_types(self):
        persona = api.content.create(container=self.portal, type="Persona", title="xxx")
        immagini = ISelectableConstrainTypes(persona["immagini"])
        self.assertEqual(immagini.getConstrainTypesMode(), 1)
        self.assertEqual(immagini.getLocallyAllowedTypes(), ["Link", "Image"])

    def test_persona_video_has_filtered_addable_types(self):
        persona = api.content.create(container=self.portal, type="Persona", title="xxx")
        video = ISelectableConstrainTypes(persona["video"])
        self.assertEqual(video.getConstrainTypesMode(), 1)
        self.assertEqual(video.getLocallyAllowedTypes(), ["Link"])

    def test_persona_curriculum_has_filtered_addable_types(self):
        persona = api.content.create(container=self.portal, type="Persona", title="xxx")
        curriculum = ISelectableConstrainTypes(persona["curriculum-vitae"])
        self.assertEqual(curriculum.getConstrainTypesMode(), 1)
        self.assertEqual(curriculum.getLocallyAllowedTypes(), ["File"])

    def test_persona_allegati_has_filtered_addable_types(self):
        persona = api.content.create(container=self.portal, type="Persona", title="xxx")
        allegati = ISelectableConstrainTypes(persona["allegati"])
        self.assertEqual(allegati.getConstrainTypesMode(), 1)
        self.assertEqual(allegati.getLocallyAllowedTypes(), ["File"])
