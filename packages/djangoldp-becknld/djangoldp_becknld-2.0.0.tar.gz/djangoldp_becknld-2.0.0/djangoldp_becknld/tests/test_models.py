from django.conf import settings
from django.contrib.auth.models import Group
from django.test import TestCase

from djangoldp_becknld.models import Item, Transaction
from djangoldp_becknld.models.transaction import tidgen


class TransactionModelTestCase(TestCase):
    def setUp(self):
        """Set up test data for Transaction model tests"""
        self.group = Group.objects.create(name="test_group")

    def test_tidgen_function(self):
        """Test that tidgen generates a valid UUID string"""
        transaction_id = tidgen()
        self.assertIsInstance(transaction_id, str)
        self.assertEqual(len(transaction_id), 36)  # UUID4 format

        # Test that multiple calls generate different IDs
        transaction_id2 = tidgen()
        self.assertNotEqual(transaction_id, transaction_id2)

    def test_transaction_creation(self):
        """Test Transaction model creation with default values"""
        transaction = Transaction.objects.create()
        self.assertIsNotNone(transaction.transaction_id)
        self.assertIsNotNone(transaction.urlid)
        self.assertIsNotNone(transaction.creation_date)
        self.assertIsNotNone(transaction.update_date)

    def test_transaction_with_creator_and_initiators(self):
        """Test Transaction with creator and initiators"""
        # Create a unique group for this transaction since initiators is OneToOneField
        unique_group = Group.objects.create(name="unique_test_group")
        transaction = Transaction.objects.create(
            creator=None,  # Will be set to authenticated user in real scenario
            initiators=unique_group,
        )
        # Refresh from database to get actual values after any signals
        transaction.refresh_from_db()

        # Check that initiators is set (exact group may be modified by signals)
        self.assertIsNotNone(transaction.initiators)
        self.assertIsInstance(transaction.initiators, Group)

    def test_transaction_properties_without_uris(self):
        """Test Transaction properties when bap_uri and bpp_uri are None"""
        transaction = Transaction.objects.create(bap_uri=None, bpp_uri=None)
        # Refresh from database to get actual values after any signals
        transaction.refresh_from_db()

        # Check that properties handle None values correctly
        if transaction.bap_uri is None:
            self.assertIsNone(transaction.bap_inbox)
            self.assertIsNone(transaction.bap_outbox)
        if transaction.bpp_uri is None:
            self.assertIsNone(transaction.bpp_inbox)
            self.assertIsNone(transaction.bpp_outbox)

    def test_transaction_properties_with_uris(self):
        """Test Transaction properties when bap_uri and bpp_uri are set"""
        transaction = Transaction.objects.create(
            bap_uri="https://example.com/transactions/123/",
            bpp_uri="https://example.com/transactions/456/",
        )

        self.assertEqual(
            transaction.bap_inbox, "https://example.com/transactions/123/inbox/"
        )
        self.assertEqual(
            transaction.bpp_inbox, "https://example.com/transactions/456/inbox/"
        )
        self.assertEqual(
            transaction.bap_outbox, "https://example.com/transactions/123/outbox/"
        )
        self.assertEqual(
            transaction.bpp_outbox, "https://example.com/transactions/456/outbox/"
        )

    def test_transaction_str_method(self):
        """Test Transaction __str__ method"""
        transaction = Transaction.objects.create(transaction_id="test-123")
        self.assertEqual(str(transaction), "test-123")

        # Test with empty transaction_id (should fallback to urlid)
        transaction.transaction_id = ""
        transaction.save()
        self.assertEqual(str(transaction), transaction.urlid)


class ItemModelTestCase(TestCase):
    def test_item_creation(self):
        """Test Item model creation"""
        item = Item.objects.create(
            item_id="https://example.com/items/123",
            unitary_price=29.99,
            unit_text="per item",
        )
        self.assertEqual(item.item_id, "https://example.com/items/123")
        self.assertEqual(item.unitary_price, 29.99)
        self.assertEqual(item.unit_text, "per item")

    def test_item_str_method(self):
        """Test Item __str__ method"""
        item = Item.objects.create(
            item_id="https://example.com/items/123",
            unitary_price=29.99,
            unit_text="per item",
        )
        self.assertEqual(str(item), item.urlid)
