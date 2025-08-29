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


class TestDocumentoSchema(unittest.TestCase):
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

    def test_behaviors_enabled_for_documento(self):
        portal_types = api.portal.get_tool(name="portal_types")
        self.assertEqual(
            portal_types["Documento"].behaviors,
            (
                "plone.namefromtitle",
                "plone.allowdiscussion",
                "plone.excludefromnavigation",
                "plone.shortname",
                "plone.ownership",
                "plone.publication",
                "plone.categorization",
                "plone.basic",
                "plone.locking",
                "plone.constraintypes",
                "plone.leadimage",
                "volto.preview_image",
                "plone.relateditems",
                "plone.textindexer",
                "plone.translatable",
                "kitconcept.seo",
                "plone.versioning",
                "iosanita.contenttypes.behavior.a_chi_si_rivolge",
                "collective.taxonomy.generated.a_chi_si_rivolge_tassonomia",
                "collective.taxonomy.generated.parliamo_di",
            ),
        )

    def test_documento_fieldsets(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Documento").json()
        self.assertEqual(len(resp["fieldsets"]), 9)
        self.assertEqual(
            [x.get("id") for x in resp["fieldsets"]],
            [
                "default",
                "cosa_e",
                "riferimenti",
                "a_chi_si_rivolge",
                "settings",
                "ownership",
                "dates",
                "categorization",
                "seo",
            ],
        )

    def test_documento_required_fields(self):
        resp = self.api_session.get("@types/Documento").json()
        self.assertEqual(
            sorted(resp["required"]),
            sorted(
                [
                    "title",
                    "descrizione_estesa",
                    "uo_correlata",
                ]
            ),
        )

    def test_documento_fields_default_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Documento").json()
        self.assertEqual(
            resp["fieldsets"][0]["fields"],
            [
                "title",
                "description",
                "protocollo",
                "data_protocollo",
                "image",
                "image_caption",
                "preview_image",
                "preview_caption",
                "parliamo_di",
            ],
        )

    def test_documento_cosa_e_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Documento").json()
        self.assertEqual(
            resp["fieldsets"][1]["fields"],
            ["descrizione_estesa"],
        )

    def test_documento_riferimenti_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Documento").json()
        self.assertEqual(
            resp["fieldsets"][2]["fields"],
            [
                "servizio_procedura_riferimento",
                "uo_correlata",
                "autori",
            ],
        )

    def test_documento_fields_a_chi_si_rivolge_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Documento").json()
        self.assertEqual(
            resp["fieldsets"][3]["fields"],
            ["a_chi_si_rivolge", "a_chi_si_rivolge_tassonomia"],
        )


class TestDocumento(unittest.TestCase):
    """"""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_documento_default_children(self):
        documento = api.content.create(
            container=self.portal, type="Documento", title="xxx"
        )

        self.assertEqual(documento.keys(), ["immagini"])

    def test_documento_immagini_has_filtered_addable_types(self):
        documento = api.content.create(
            container=self.portal, type="Documento", title="xxx"
        )
        immagini = ISelectableConstrainTypes(documento["immagini"])
        self.assertEqual(immagini.getConstrainTypesMode(), 1)
        self.assertEqual(immagini.getLocallyAllowedTypes(), ["Link", "Image"])
