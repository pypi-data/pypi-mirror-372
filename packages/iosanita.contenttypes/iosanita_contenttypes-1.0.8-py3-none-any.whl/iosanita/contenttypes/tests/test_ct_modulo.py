# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from iosanita.contenttypes.testing import RESTAPI_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession

import unittest


class TestModuloSchema(unittest.TestCase):
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

    def test_behaviors_enabled_for_modulo(self):
        portal_types = api.portal.get_tool(name="portal_types")
        self.assertEqual(
            portal_types["Modulo"].behaviors,
            (
                "plone.namefromtitle",
                "plone.allowdiscussion",
                "plone.excludefromnavigation",
                "plone.shortname",
                "plone.dublincore",
                "plone.relateditems",
                "plone.locking",
                "iosanita.contenttypes.behavior.multi_file",
                "plone.translatable",
                "volto.enhanced_links_enabled",
            ),
        )

    def test_modulo_fieldsets(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Modulo").json()
        self.assertEqual(len(resp["fieldsets"]), 6)
        self.assertEqual(
            [x.get("id") for x in resp["fieldsets"]],
            [
                "default",
                "formati",
                "settings",
                "categorization",
                "dates",
                "ownership",
            ],
        )

    def test_modulo_required_fields(self):
        resp = self.api_session.get("@types/Modulo").json()
        self.assertEqual(
            sorted(resp["required"]),
            sorted(
                [
                    "title",
                    "file",
                ]
            ),
        )

    def test_modulo_fields_default_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Modulo").json()
        self.assertEqual(
            resp["fieldsets"][0]["fields"],
            [
                "title",
                "description",
            ],
        )

    def test_modulo_formati_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Modulo").json()
        self.assertEqual(
            resp["fieldsets"][1]["fields"],
            ["file", "formato_alternativo_1", "formato_alternativo_2"],
        )
