# -*- coding: utf-8 -*-

from iosanita.contenttypes.testing import RESTAPI_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession

import unittest


class TestDocumentSchema(unittest.TestCase):
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

    def test_behaviors_enabled_for_document(self):
        portal_types = api.portal.get_tool(name="portal_types")
        self.assertEqual(
            portal_types["Document"].behaviors,
            (
                "plone.namefromtitle",
                "plone.allowdiscussion",
                "plone.excludefromnavigation",
                "plone.shortname",
                "plone.dublincore",
                "plone.relateditems",
                "plone.locking",
                "volto.blocks",
                "volto.preview_image",
                "plone.versioning",
                "plone.tableofcontents",
                "iosanita.contenttypes.behavior.info_testata",
                "iosanita.contenttypes.behavior.argomenti_document",
                "plone.translatable",
                "iosanita.contenttypes.behavior.show_modified",
                "kitconcept.seo",
                "plone.constraintypes",
                "plone.leadimage",
                "iosanita.contenttypes.behavior.exclude_from_search",
                "collective.taxonomy.generated.parliamo_di",
            ),
        )

    def test_document_fieldsets(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Document").json()
        self.assertEqual(len(resp["fieldsets"]), 9)
        self.assertEqual(
            [x.get("id") for x in resp["fieldsets"]],
            [
                "default",
                "testata",
                "settings",
                "correlati",
                "categorization",
                "dates",
                "ownership",
                "seo",
                "layout",
            ],
        )

    def test_document_required_fields(self):
        resp = self.api_session.get("@types/Document").json()
        self.assertEqual(
            sorted(resp["required"]),
            sorted(["title"]),
        )

    def test_document_fields_default_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Document").json()
        self.assertEqual(
            resp["fieldsets"][0]["fields"],
            [
                "title",
                "description",
                "preview_image",
                "preview_caption",
                "image",
                "image_caption",
                "parliamo_di",
            ],
        )

    def test_document_fields_testata_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Document").json()
        self.assertEqual(
            resp["fieldsets"][1]["fields"],
            [
                "ricerca_in_testata",
                "mostra_bottoni_condivisione",
                "info_testata",
            ],
        )

    def test_document_fields_settings_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Document").json()
        self.assertEqual(
            resp["fieldsets"][2]["fields"],
            [
                "allow_discussion",
                "exclude_from_nav",
                "id",
                "versioning_enabled",
                "table_of_contents",
                "show_modified",
                "exclude_from_search",
                "changeNote",
            ],
        )

    def test_document_fields_correlati_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Document").json()
        self.assertEqual(
            resp["fieldsets"][3]["fields"],
            ["correlato_in_evidenza"],
        )

    def test_document_fields_categorization_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Document").json()
        self.assertEqual(
            resp["fieldsets"][4]["fields"], ["subjects", "language", "relatedItems"]
        )

    def test_document_fields_dates_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Document").json()
        self.assertEqual(resp["fieldsets"][5]["fields"], ["effective", "expires"])

    def test_document_fields_ownership_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Document").json()
        self.assertEqual(
            resp["fieldsets"][6]["fields"], ["creators", "contributors", "rights"]
        )

    def test_document_fields_seo_fieldset(self):
        """
        Get the list from restapi
        """
        resp = self.api_session.get("@types/Document").json()
        self.assertEqual(
            resp["fieldsets"][7]["fields"],
            [
                "seo_title",
                "seo_description",
                "seo_noindex",
                "seo_canonical_url",
                "opengraph_title",
                "opengraph_description",
                "opengraph_image",
            ],
        )
