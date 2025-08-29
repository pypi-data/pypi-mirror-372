# -*- coding: utf-8 -*-
from pas.plugins.imio.testing import PAS_PLUGINS_IMIO_FUNCTIONAL_TESTING
from plone import api

import unittest


TEST_ID_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkU5WG1fOExtd3FuQ1hFalJPTzV3M19NdlZTRDQ1RzFIOTN3QU5JUWRlSUUifQ.eyJhY3IiOiIwIiwiYXVkIjoiY2xpZW50LWlkLXBsb25lNS1hcHAiLCJhdXRoX3RpbWUiOjE2MTc5NzI2ODIsImV4cCI6MTYxNzk3MjcxMiwiaWF0IjoxNjE3OTcyNjgyLCJpc3MiOiJodHRwOi8vYWdlbnRzLndjLmxvY2FsaG9zdC8iLCJzdWIiOiJjYTEzMmE0NGJjMmI0ODhhOTExZjJhYWExNzg4NmMwYSIsInVzZXJpZCI6Impkb2UifQ.HztAdBSTGqXeCL3Io8E2TXi5mdoxcwD52IOqoEdp4TBetF7GgwXNgJxjYFNu7p65m_5ApZBJEnrWKumnNh9g7j4-XhTNt1Cz_s3pq7U4GpRZ8ymfSkG8MUist806kqER8jYq6HguPDjFPFEF4qf2uo1IDcZSySpDOQr9JJ69ux2O-CECmxaF4DRGDN9IX34mLX_qezY4K56jZx90D5KjjAHFWcTLxRWw6IsvnB6Rmdsp4aZHWhLIuzhNnlKHxed7JY5HTZDEn0jqkRSFchhp-vPzQV9hwk17JFz5Q3uf3pJqaKt1onDD5s4nn3LEysDIt01YEd-UUrKXy4vgCVMvAg"  # noqa


class TestPAS(unittest.TestCase):

    layer = PAS_PLUGINS_IMIO_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.acl_users = api.portal.get_tool("acl_users")
        self.plugin = self.acl_users["authentic"]

    def test_extract_credentials_with_bearer_authorization_header(self):
        request = self.layer["request"]
        request._auth = (
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9."
            "PGnRccPTXeaxA8nzfytWewWRkizJa_ihI_3H6ec-Zbw"
        )
        self.assertEqual(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9.PGnRccP"
            "TXeaxA8nzfytWewWRkizJa_ihI_3H6ec-Zbw",
            self.plugin.extractCredentials(request)["token"],
        )

    def test_authenticate_credentials_from_unknown_extractor(self):
        creds = {}
        creds["extractor"] = "credentials_basic_auth"
        self.assertEqual(None, self.plugin.authenticateCredentials(creds))

    def test_authenticate_credentials_with_valid_token(self):
        creds = {}
        creds["extractor"] = "authentic"
        creds["token"] = TEST_ID_TOKEN
        self.assertEqual(
            ("ca132a44bc2b488a911f2aaa17886c0a", "jdoe"),
            self.plugin.authenticateCredentials(creds),
        )

    def test_creation_of_user_with_valid_token(self):
        creds = {}
        creds["extractor"] = "authentic"
        creds["token"] = TEST_ID_TOKEN
        userid, username = self.plugin.authenticateCredentials(creds)
        self.assertEqual("jdoe", self.plugin.getPluginUsers()[0]["login"])
        self.assertEqual(
            "authentic-agents", self.plugin.getPluginUsers()[0]["plugin_type"]
        )
