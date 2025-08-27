from django.test import TestCase
from djangoldp.activities import errors

from djangoldp_becknld.activities.verbs import (BecknLDActivity,
                                                BecknLDConfirm, BecknLDInit,
                                                BecknLDOnConfirm,
                                                BecknLDOnInit, BecknLDOnSelect,
                                                BecknLDSelect)


class BecknLDActivityTestCase(TestCase):
    def setUp(self):
        """Set up test data for BecknLD activities"""
        self.valid_actor = {"@id": "https://example.com/actor/123"}
        self.valid_object = {"@type": "beckn:Item", "name": "Test Item"}

    def test_becknld_activity_creation(self):
        """Test basic BecknLDActivity creation"""
        activity = BecknLDActivity()
        self.assertEqual(activity.type, "BecknLDActivity")
        self.assertIn("@type", activity.attributes)
        self.assertIn("as:actor", activity.attributes)
        self.assertIn("as:target", activity.attributes)
        self.assertIn("as:object", activity.attributes)
        self.assertIn("beckn:context", activity.attributes)

    def test_becknld_activity_validation_success(self):
        """Test BecknLDActivity validation with valid data"""
        activity = BecknLDActivity()
        setattr(activity, 'as:actor', self.valid_actor)
        setattr(activity, 'as:object', self.valid_object)

        # Should not raise an exception
        try:
            activity.validate()
        except errors.ActivityStreamValidationError:
            self.fail("validate() raised ActivityStreamValidationError unexpectedly")

    def test_becknld_activity_validation_missing_actor(self):
        """Test BecknLDActivity validation with missing actor"""
        activity = BecknLDActivity()
        setattr(activity, 'as:object', self.valid_object)

        with self.assertRaises(errors.ActivityStreamValidationError) as context:
            activity.validate()

        self.assertIn("as:actor", str(context.exception))

    def test_becknld_activity_validation_missing_object(self):
        """Test BecknLDActivity validation with missing object"""
        activity = BecknLDActivity()
        setattr(activity, 'as:actor', self.valid_actor)

        with self.assertRaises(errors.ActivityStreamValidationError) as context:
            activity.validate()

        self.assertIn("as:object", str(context.exception))

    def test_becknld_activity_validation_wrong_actor_type(self):
        """Test BecknLDActivity validation with wrong actor type"""
        activity = BecknLDActivity()
        setattr(activity, 'as:actor', "invalid_actor")  # Should be dict
        setattr(activity, 'as:object', self.valid_object)

        with self.assertRaises(errors.ActivityStreamValidationError) as context:
            activity.validate()

        self.assertIn("as:actor", str(context.exception))

    def test_becknld_activity_validation_wrong_object_type(self):
        """Test BecknLDActivity validation with wrong object type"""
        activity = BecknLDActivity()
        setattr(activity, 'as:actor', self.valid_actor)
        setattr(activity, 'as:object', "invalid_object")  # Should be dict

        with self.assertRaises(errors.ActivityStreamValidationError) as context:
            activity.validate()

        self.assertIn("as:object", str(context.exception))


class SpecificActivityTypesTestCase(TestCase):
    def test_select_activity_type(self):
        """Test BecknLDSelect has correct type"""
        activity = BecknLDSelect()
        self.assertEqual(activity.type, "select")

    def test_init_activity_type(self):
        """Test BecknLDInit has correct type"""
        activity = BecknLDInit()
        self.assertEqual(activity.type, "init")

    def test_confirm_activity_type(self):
        """Test BecknLDConfirm has correct type"""
        activity = BecknLDConfirm()
        self.assertEqual(activity.type, "confirm")

    def test_on_select_activity_type(self):
        """Test BecknLDOnSelect has correct type"""
        activity = BecknLDOnSelect()
        self.assertEqual(activity.type, "on_select")

    def test_on_init_activity_type(self):
        """Test BecknLDOnInit has correct type"""
        activity = BecknLDOnInit()
        self.assertEqual(activity.type, "on_init")

    def test_on_confirm_activity_type(self):
        """Test BecknLDOnConfirm has correct type"""
        activity = BecknLDOnConfirm()
        self.assertEqual(activity.type, "on_confirm")

    def test_all_activities_inherit_validation(self):
        """Test that all specific activity types inherit validation behavior"""
        activities = [
            BecknLDSelect(),
            BecknLDInit(),
            BecknLDConfirm(),
            BecknLDOnSelect(),
            BecknLDOnInit(),
            BecknLDOnConfirm(),
        ]

        for activity in activities:
            # Each should have the validate method
            self.assertTrue(hasattr(activity, "validate"))
            self.assertTrue(callable(getattr(activity, "validate")))

            # Each should inherit from BecknLDActivity
            self.assertIsInstance(activity, BecknLDActivity)
