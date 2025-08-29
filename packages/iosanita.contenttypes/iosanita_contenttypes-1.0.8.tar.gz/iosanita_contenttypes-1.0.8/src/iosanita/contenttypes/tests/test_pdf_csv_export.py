from ..testing import INTEGRATION_TESTING
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing.z2 import Browser
from transaction import commit
from zope.component import getMultiAdapter

import csv
import unittest
import uuid


class TestExport(unittest.TestCase):
    """Test PDF export functionality"""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)

        self.doc = api.content.create(
            container=self.portal,
            type="Document",
            id="test-document",
            title="Test Document",
            description="This is a test document",
        )
        api.content.transition(self.doc, to_state="published")
        commit()

        self.browser = Browser(self.app)

    def tearDown(self):
        api.content.delete(self.doc)
        commit()
        logout()

    def test_pdf_export_view_exists(self):
        """Test that the PDF export view is registered and accessible

        TODO: view must be accessible only for IExportViewDownload context
        """
        view = getMultiAdapter((self.doc, self.request), name="export_pdf")
        self.assertTrue(view is not None)

    def test_searchblock_pdf(self):
        block_id = uuid.uuid4().hex
        self.doc.blocks = {
            block_id: {
                "@type": "search",
                "query": {
                    "query": [
                        {
                            "i": "portal_type",
                            "o": "plone.app.querystring.operation.selection.is",
                            "v": "Document",
                        }
                    ]
                },
            }
        }
        self.doc.blocks_layout = {"items": [block_id]}
        commit()

        self.browser.open(
            f"{self.doc.absolute_url()}/searchblock/@@download/{block_id}.pdf"
        )

        # Check response headers
        self.assertEqual(self.browser.headers["Content-Type"], "application/pdf")
        self.assertIn(
            "attachment;filename=", self.browser.headers["Content-Disposition"]
        )
        # Check that the response is not empty and looks like a PDF
        self.assertTrue(b"%PDF-" in self.browser.contents[:10])

        # TODO
        # api.portal.get_tool("portal_transforms").convertTo("plain/text", self.browser.contents, mimetype="application/pdf")
        # oppure con pypdf

    def test_searchblock_csv(self):
        block_id = uuid.uuid4().hex
        self.doc.blocks = {
            block_id: {
                "@type": "search",
                "query": {
                    "query": [
                        {
                            "i": "portal_type",
                            "o": "plone.app.querystring.operation.selection.is",
                            "v": "Document",
                        }
                    ]
                },
            }
        }
        self.doc.blocks_layout = {"items": [block_id]}
        commit()

        self.browser.open(
            f"{self.doc.absolute_url()}/searchblock/@@download/{block_id}.csv"
        )

        # Check response headers
        self.assertEqual(
            self.browser.headers["Content-Type"], "text/csv; charset=utf-8-sig"
        )
        self.assertIn(
            "attachment;filename=", self.browser.headers["Content-Disposition"]
        )

        # Check that the response is a CSV with expected data
        reader = csv.DictReader(self.browser.contents)
        self.assertEqual(reader.fieldnames, ["Titolo"])
        self.assertEqual([row for row in reader], [{"Titolo": "Test Document"}])
