"""
Unit tests for BMI Calculator core logic and database operations.
Run with: python -m pytest tests/test_bmi.py -v
Or: python tests/test_bmi.py
"""

import unittest
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bmi_core import calculate_bmi, classify_bmi, validate_input, get_category_color
from database import BMIDatabase


class TestBMICalculation(unittest.TestCase):
    """Test BMI calculation logic."""

    def test_basic_calculation(self):
        """Test basic BMI calculation."""
        bmi = calculate_bmi(70, 1.75)
        self.assertEqual(bmi, 22.86)

    def test_calculation_rounding(self):
        """Test that BMI is rounded to 2 decimal places."""
        bmi = calculate_bmi(80.5, 1.80)
        self.assertEqual(bmi, 24.85)

    def test_low_bmi(self):
        """Test calculation with low BMI values."""
        bmi = calculate_bmi(50, 1.70)
        self.assertEqual(bmi, 17.30)

    def test_high_bmi(self):
        """Test calculation with high BMI values."""
        bmi = calculate_bmi(100, 1.65)
        self.assertEqual(bmi, 36.73)


class TestBMIClassification(unittest.TestCase):
    """Test BMI classification logic."""

    def test_underweight_boundary(self):
        """Test underweight category boundary."""
        self.assertEqual(classify_bmi(18.4), "Underweight")
        self.assertEqual(classify_bmi(18.49), "Underweight")
        self.assertEqual(classify_bmi(10.0), "Underweight")

    def test_normal_lower_boundary(self):
        """Test normal category lower boundary."""
        self.assertEqual(classify_bmi(18.5), "Normal")
        self.assertEqual(classify_bmi(18.50), "Normal")

    def test_normal_upper_boundary(self):
        """Test normal category upper boundary."""
        self.assertEqual(classify_bmi(24.9), "Normal")
        self.assertEqual(classify_bmi(24.99), "Normal")

    def test_overweight_lower_boundary(self):
        """Test overweight category lower boundary."""
        self.assertEqual(classify_bmi(25.0), "Overweight")
        self.assertEqual(classify_bmi(25.00), "Overweight")

    def test_overweight_upper_boundary(self):
        """Test overweight category upper boundary."""
        self.assertEqual(classify_bmi(29.9), "Overweight")
        self.assertEqual(classify_bmi(29.99), "Overweight")

    def test_obese_boundary(self):
        """Test obese category boundary."""
        self.assertEqual(classify_bmi(30.0), "Obese")
        self.assertEqual(classify_bmi(30.00), "Obese")
        self.assertEqual(classify_bmi(40.0), "Obese")
        self.assertEqual(classify_bmi(50.0), "Obese")


class TestInputValidation(unittest.TestCase):
    """Test input validation logic."""

    def test_valid_input(self):
        """Test valid input."""
        valid, msg, weight, height = validate_input("70", "1.75")
        self.assertTrue(valid)
        self.assertEqual(msg, "")
        self.assertEqual(weight, 70.0)
        self.assertEqual(height, 1.75)

    def test_empty_weight(self):
        """Test empty weight input."""
        valid, msg, _, _ = validate_input("", "1.75")
        self.assertFalse(valid)
        self.assertIn("weight", msg.lower())

    def test_empty_height(self):
        """Test empty height input."""
        valid, msg, _, _ = validate_input("70", "")
        self.assertFalse(valid)
        self.assertIn("height", msg.lower())

    def test_non_numeric_weight(self):
        """Test non-numeric weight input."""
        valid, msg, _, _ = validate_input("abc", "1.75")
        self.assertFalse(valid)
        self.assertIn("weight", msg.lower())
        self.assertIn("number", msg.lower())

    def test_non_numeric_height(self):
        """Test non-numeric height input."""
        valid, msg, _, _ = validate_input("70", "xyz")
        self.assertFalse(valid)
        self.assertIn("height", msg.lower())
        self.assertIn("number", msg.lower())

    def test_negative_weight(self):
        """Test negative weight."""
        valid, msg, _, _ = validate_input("-70", "1.75")
        self.assertFalse(valid)
        self.assertIn("greater than zero", msg.lower())

    def test_zero_weight(self):
        """Test zero weight."""
        valid, msg, _, _ = validate_input("0", "1.75")
        self.assertFalse(valid)
        self.assertIn("greater than zero", msg.lower())

    def test_negative_height(self):
        """Test negative height."""
        valid, msg, _, _ = validate_input("70", "-1.75")
        self.assertFalse(valid)
        self.assertIn("greater than zero", msg.lower())

    def test_zero_height(self):
        """Test zero height."""
        valid, msg, _, _ = validate_input("70", "0")
        self.assertFalse(valid)
        self.assertIn("greater than zero", msg.lower())

    def test_unrealistic_weight(self):
        """Test unrealistic weight (too high)."""
        valid, msg, _, _ = validate_input("600", "1.75")
        self.assertFalse(valid)
        self.assertIn("realistic", msg.lower())

    def test_unrealistic_height_high(self):
        """Test unrealistic height (too high)."""
        valid, msg, _, _ = validate_input("70", "5.0")
        self.assertFalse(valid)
        self.assertIn("metres", msg.lower())

    def test_unrealistic_height_low(self):
        """Test unrealistic height (too low)."""
        valid, msg, _, _ = validate_input("70", "0.3")
        self.assertFalse(valid)
        self.assertIn("realistic", msg.lower())

    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        valid, msg, weight, height = validate_input("  70  ", "  1.75  ")
        self.assertTrue(valid)
        self.assertEqual(weight, 70.0)
        self.assertEqual(height, 1.75)


class TestCategoryColors(unittest.TestCase):
    """Test category color mappings."""

    def test_all_categories_have_colors(self):
        """Test that all categories have color mappings."""
        self.assertNotEqual(get_category_color("Underweight"), "#000000")
        self.assertNotEqual(get_category_color("Normal"), "#000000")
        self.assertNotEqual(get_category_color("Overweight"), "#000000")
        self.assertNotEqual(get_category_color("Obese"), "#000000")

    def test_color_format(self):
        """Test that colors are in hex format."""
        for category in ["Underweight", "Normal", "Overweight", "Obese"]:
            color = get_category_color(category)
            self.assertTrue(color.startswith("#"))
            self.assertEqual(len(color), 7)


class TestDatabase(unittest.TestCase):
    """Test database operations."""

    def setUp(self):
        """Set up test database before each test."""
        self.test_db_path = "test_bmi.db"
        self.db = BMIDatabase(self.test_db_path)

    def tearDown(self):
        """Clean up test database after each test."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_database_creation(self):
        """Test that database file is created."""
        self.assertTrue(os.path.exists(self.test_db_path))

    def test_save_record(self):
        """Test saving a BMI record."""
        success = self.db.save_record("John", 70.0, 1.75, 22.86, "Normal")
        self.assertTrue(success)

    def test_get_user_history(self):
        """Test retrieving user history."""
        # Save some records
        self.db.save_record("Alice", 60.0, 1.65, 22.04, "Normal")
        self.db.save_record("Alice", 62.0, 1.65, 22.77, "Normal")

        # Get history
        records = self.db.get_user_history("Alice")
        self.assertEqual(len(records), 2)

        # Check that records are for the correct user
        for record in records:
            self.assertEqual(record[1], "Alice")

    def test_user_separation(self):
        """Test that different users' records are kept separate."""
        # Save records for different users
        self.db.save_record("Alice", 60.0, 1.65, 22.04, "Normal")
        self.db.save_record("Bob", 80.0, 1.80, 24.69, "Normal")
        self.db.save_record("Alice", 62.0, 1.65, 22.77, "Normal")

        # Check Alice's records
        alice_records = self.db.get_user_history("Alice")
        self.assertEqual(len(alice_records), 2)

        # Check Bob's records
        bob_records = self.db.get_user_history("Bob")
        self.assertEqual(len(bob_records), 1)

    def test_get_all_users(self):
        """Test retrieving all unique users."""
        # Save records for different users
        self.db.save_record("Alice", 60.0, 1.65, 22.04, "Normal")
        self.db.save_record("Bob", 80.0, 1.80, 24.69, "Normal")
        self.db.save_record("Alice", 62.0, 1.65, 22.77, "Normal")

        # Get all users
        users = self.db.get_all_users()
        self.assertEqual(len(users), 2)
        self.assertIn("Alice", users)
        self.assertIn("Bob", users)

    def test_record_count(self):
        """Test getting record count for a user."""
        # Save records
        self.db.save_record("Charlie", 70.0, 1.75, 22.86, "Normal")
        self.db.save_record("Charlie", 71.0, 1.75, 23.18, "Normal")
        self.db.save_record("Charlie", 72.0, 1.75, 23.51, "Normal")

        # Check count
        count = self.db.get_record_count("Charlie")
        self.assertEqual(count, 3)

    def test_empty_history(self):
        """Test getting history for user with no records."""
        records = self.db.get_user_history("NonExistent")
        self.assertEqual(len(records), 0)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
