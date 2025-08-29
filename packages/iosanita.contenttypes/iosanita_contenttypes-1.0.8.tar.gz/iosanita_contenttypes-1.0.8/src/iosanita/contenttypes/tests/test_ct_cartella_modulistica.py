# -*- coding: utf-8 -*-
"""Setup tests for this package."""
# from iosanita.contenttypes.testing import INTEGRATION_TESTING
from iosanita.contenttypes.testing import RESTAPI_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from transaction import commit

import unittest


# from Products.CMFPlone.interfaces import ISelectableConstrainTypes


class TestCartellaModulisticaSchema(unittest.TestCase):
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

        self.cartella_modulistica = api.content.create(
            container=self.portal, type="CartellaModulistica", title="cm"
        )
        commit()

    def tearDown(self):
        self.api_session.close()

    def test_behaviors_enabled_for_cartella_modulistica(self):
        portal_types = api.portal.get_tool(name="portal_types")
        self.assertEqual(
            portal_types["CartellaModulistica"].behaviors,
            (
                "plone.namefromtitle",
                "plone.allowdiscussion",
                "plone.excludefromnavigation",
                "plone.shortname",
                "plone.ownership",
                "plone.publication",
                "plone.categorization",
                "plone.basic",
                "plone.leadimage",
                "volto.preview_image",
                "plone.locking",
                "volto.blocks",
                "plone.translatable",
                "kitconcept.seo",
                "plone.versioning",
            ),
        )

    def test_cartella_modulistica_fieldsets(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/CartellaModulistica").json()
        self.assertEqual(len(resp["fieldsets"]), 7)
        self.assertEqual(
            [x.get("id") for x in resp["fieldsets"]],
            [
                "default",
                "settings",
                "ownership",
                "dates",
                "categorization",
                "layout",
                "seo",
            ],
        )

    def test_cartella_modulistica_required_fields(self):
        resp = self.api_session.get("@types/CartellaModulistica").json()
        self.assertEqual(
            sorted(resp["required"]),
            sorted(
                [
                    "title",
                ]
            ),
        )

    def test_cartella_modulistica_fields_default_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/CartellaModulistica").json()
        self.assertEqual(
            resp["fieldsets"][0]["fields"],
            [
                "title",
                "description",
                "anteprima_file",
                "ricerca_in_testata",
                "image",
                "image_caption",
                "preview_image",
                "preview_caption",
            ],
        )

    def test_cartella_modulistica_expander(self):
        api.content.create(
            container=self.cartella_modulistica, type="File", title="xxx"
        )
        commit()

        resp = self.api_session.get("/cm/@modulistica-items").json()["items"][0]
        self.assertEqual(resp["@type"], "File")
        self.assertEqual(resp["id"], "xxx")
