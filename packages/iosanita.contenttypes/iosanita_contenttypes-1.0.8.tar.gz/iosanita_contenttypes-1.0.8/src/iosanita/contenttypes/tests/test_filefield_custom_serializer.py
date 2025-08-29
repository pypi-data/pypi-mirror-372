# -*- coding: utf-8 -*-
from iosanita.contenttypes.testing import RESTAPI_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from plone.restapi.testing import RelativeSession
from transaction import commit

import unittest


class FileFieldSerializerTest(unittest.TestCase):
    layer = RESTAPI_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.cartella_modulistica = api.content.create(
            container=self.portal,
            type="CartellaModulistica",
            title="Cartella Modulistica",
        )
        self.document = api.content.create(
            container=self.cartella_modulistica, type="Documento", title="Document"
        )
        self.modulo = api.content.create(
            container=self.document,
            type="Modulo",
            title="Modulo",
            file=NamedBlobFile("some data", filename="file.pdf"),
        )
        commit()

    def tearDown(self):
        self.api_session.close()

    def test_if_anteprima_file_false_so_download(self):
        response = self.api_session.get(self.modulo.absolute_url()).json()

        self.assertIn("@@download", response["file"]["download"])

    def test_if_anteprima_file_true_so_dsiplay(self):
        self.cartella_modulistica.anteprima_file = True

        commit()

        response = self.api_session.get(self.modulo.absolute_url()).json()
        self.assertIn("@@display-file", response["file"]["download"])

    def test_if_enhancedlinks_behavior_active_has_human_readable_obj_size_in_data(self):
        response = self.api_session.get(self.modulo.absolute_url()).json()
        self.assertEqual("1 KB", response["file"]["getObjSize"])

    def test_if_enhancedlinks_behavior_active_has_flag_in_data(self):
        response = self.api_session.get(self.modulo.absolute_url()).json()
        self.assertIn("enhanced_links_enabled", response["file"])
        self.assertTrue(response["file"]["enhanced_links_enabled"])
