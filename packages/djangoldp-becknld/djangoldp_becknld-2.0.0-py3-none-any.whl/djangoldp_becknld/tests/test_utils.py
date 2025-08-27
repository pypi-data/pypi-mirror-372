from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.test.utils import override_settings

from djangoldp_becknld.models.transaction import tidgen


class UtilsTestCase(TestCase):
    def test_tidgen_returns_string(self):
        """Test that tidgen returns a string"""
        result = tidgen()
        self.assertIsInstance(result, str)

    def test_tidgen_returns_valid_uuid_format(self):
        """Test that tidgen returns a valid UUID4 format string"""
        result = tidgen()
        # UUID4 format is xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (36 characters)
        self.assertEqual(len(result), 36)
        # Should have dashes at positions 8, 13, 18, 23
        self.assertEqual(result[8], "-")
        self.assertEqual(result[13], "-")
        self.assertEqual(result[18], "-")
        self.assertEqual(result[23], "-")

    def test_tidgen_uniqueness(self):
        """Test that tidgen generates unique values"""
        results = [tidgen() for _ in range(100)]
        unique_results = set(results)
        self.assertEqual(
            len(results), len(unique_results), "tidgen should generate unique values"
        )


class SettingsTestCase(TestCase):
    @override_settings(DEBUG=True)
    def test_settings_override_works(self):
        """Test that Django settings can be overridden in tests"""
        from django.conf import settings

        self.assertTrue(settings.DEBUG)

    def test_default_settings_access(self):
        """Test that we can access default Django settings"""
        from django.conf import settings

        # This should not raise an exception
        self.assertIsNotNone(settings.SECRET_KEY)
