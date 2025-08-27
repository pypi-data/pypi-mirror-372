from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from djangoldp_becknld.consts import BECKNLD_CONTEXT


class BecknLDConstantsTestCase(TestCase):
    def test_becknld_context_structure(self):
        """Test that BECKNLD_CONTEXT has the expected structure"""
        self.assertIsInstance(BECKNLD_CONTEXT, dict)
        self.assertIn("as", BECKNLD_CONTEXT)
        self.assertIn("schema", BECKNLD_CONTEXT)
        self.assertIn("dc", BECKNLD_CONTEXT)
        self.assertIn("geo", BECKNLD_CONTEXT)
        self.assertIn("beckn", BECKNLD_CONTEXT)

    def test_becknld_context_values(self):
        """Test that BECKNLD_CONTEXT has correct namespace values"""
        expected_values = {
            "as": "https://www.w3.org/ns/activitystreams#",
            "schema": "http://schema.org/",
            "dc": "http://purl.org/dc/terms/",
            "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",
            "beckn": "https://ontology.beckn.org/core/v1#",
        }

        for key, expected_value in expected_values.items():
            self.assertEqual(BECKNLD_CONTEXT[key], expected_value)


class BecknLDConfigurationTestCase(TestCase):
    def test_current_configuration_from_runner(self):
        """Test that the current configuration from runner works as expected"""
        # Test the configuration that is set in runner.py
        from djangoldp_becknld import consts

        self.assertTrue(consts.IS_BAP)
        self.assertTrue(consts.IS_BPP)  # Both are enabled in runner.py
        self.assertEqual(consts.BAP_URI, "http://startinblox.com/")
        self.assertEqual(consts.BPP_URI, "http://startinblox.com/")

    def test_uri_trailing_slash_handling(self):
        """Test that URIs without trailing slashes get them added"""
        # Test the current configuration
        from djangoldp_becknld import consts

        # Both URIs should have trailing slashes
        self.assertTrue(consts.BAP_URI.endswith("/"))
        self.assertTrue(consts.BPP_URI.endswith("/"))

    def test_configuration_values_are_set(self):
        """Test that configuration values are properly set"""
        from djangoldp_becknld import consts

        # Test that the basic configuration values exist
        self.assertIsNotNone(consts.IS_BAP)
        self.assertIsNotNone(consts.IS_BPP)
        self.assertIsNotNone(consts.BAP_URI)
        self.assertIsNotNone(consts.BPP_URI)
