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


class TestComeFarePerSchema(unittest.TestCase):
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

    def test_behaviors_enabled_for_come_fare_per(self):
        portal_types = api.portal.get_tool(name="portal_types")
        self.assertEqual(
            portal_types["ComeFarePer"].behaviors,
            (
                "plone.namefromtitle",
                "plone.allowdiscussion",
                "plone.excludefromnavigation",
                "plone.shortname",
                "plone.ownership",
                "plone.publication",
                "plone.categorization",
                "iosanita.basic",
                "iosanita.contenttypes.behavior.sottotitolo",
                "plone.locking",
                "plone.leadimage",
                "volto.preview_image",
                "plone.relateditems",
                "plone.textindexer",
                "plone.translatable",
                "kitconcept.seo",
                "plone.versioning",
                "iosanita.contenttypes.behavior.a_chi_si_rivolge",
                "collective.taxonomy.generated.a_chi_si_rivolge_tassonomia",
                "iosanita.contenttypes.behavior.ulteriori_informazioni",
                "collective.taxonomy.generated.parliamo_di",
            ),
        )

    def test_come_fare_per_fieldsets(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/ComeFarePer").json()
        self.assertEqual(len(resp["fieldsets"]), 9)
        self.assertEqual(
            [x.get("id") for x in resp["fieldsets"]],
            [
                "default",
                "a_chi_si_rivolge",
                "come_fare",
                "ulteriori_informazioni",
                "settings",
                "ownership",
                "dates",
                "categorization",
                "seo",
            ],
        )

    def test_come_fare_per_required_fields(self):
        resp = self.api_session.get("@types/ComeFarePer").json()
        self.assertEqual(
            sorted(resp["required"]),
            sorted(
                [
                    "come_fare",
                    "title",
                    "description",
                    "panoramica",
                ]
            ),
        )

    def test_come_fare_per_fields_default_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/ComeFarePer").json()
        self.assertEqual(
            resp["fieldsets"][0]["fields"],
            [
                "title",
                "description",
                "sottotitolo",
                "panoramica",
                "image",
                "image_caption",
                "preview_image",
                "preview_caption",
                "parliamo_di",
            ],
        )

    def test_come_fare_per_fields_a_chi_si_rivolge_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/ComeFarePer").json()
        self.assertEqual(
            resp["fieldsets"][1]["fields"],
            ["a_chi_si_rivolge", "a_chi_si_rivolge_tassonomia"],
        )

    def test_come_fare_per_fields_ulteriori_info_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/ComeFarePer").json()
        self.assertEqual(resp["fieldsets"][2]["fields"], ["come_fare"])
