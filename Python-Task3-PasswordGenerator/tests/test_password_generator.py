"""
Unit tests for the Random Password Generator

Tests password generation logic, validation, character categories,
ambiguous character exclusion, and strength estimation.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from password_generator import (
    PasswordGenerator,
    InvalidLengthError,
    NoCharactersSelectedError,
    PasswordGeneratorError
)


class TestPasswordGenerator(unittest.TestCase):
    """Test suite for PasswordGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = PasswordGenerator()

    def test_minimum_valid_length(self):
        """Test password generation at minimum length."""
        password = self.generator.generate(length=8)
        self.assertEqual(len(password), 8)

    def test_maximum_valid_length(self):
        """Test password generation at maximum length."""
        password = self.generator.generate(length=128)
        self.assertEqual(len(password), 128)

    def test_typical_length(self):
        """Test password generation with typical length."""
        for length in [12, 16, 20, 24]:
            with self.subTest(length=length):
                password = self.generator.generate(length=length)
                self.assertEqual(len(password), length)

    def test_length_below_minimum(self):
        """Test that length below minimum raises error."""
        with self.assertRaises(InvalidLengthError):
            self.generator.generate(length=7)

    def test_length_above_maximum(self):
        """Test that length above maximum raises error."""
        with self.assertRaises(InvalidLengthError):
            self.generator.generate(length=129)

    def test_length_zero(self):
        """Test that zero length raises error."""
        with self.assertRaises(InvalidLengthError):
            self.generator.generate(length=0)

    def test_negative_length(self):
        """Test that negative length raises error."""
        with self.assertRaises(InvalidLengthError):
            self.generator.generate(length=-5)

    def test_non_integer_length(self):
        """Test that non-integer length raises error."""
        with self.assertRaises(InvalidLengthError):
            self.generator.generate(length="16")

    def test_uppercase_only(self):
        """Test password with only uppercase letters."""
        password = self.generator.generate(
            length=12,
            use_uppercase=True,
            use_lowercase=False,
            use_digits=False,
            use_special=False
        )
        self.assertEqual(len(password), 12)
        self.assertTrue(all(c.isupper() for c in password))
        self.assertTrue(any(c in self.generator.UPPERCASE for c in password))

    def test_lowercase_only(self):
        """Test password with only lowercase letters."""
        password = self.generator.generate(
            length=12,
            use_uppercase=False,
            use_lowercase=True,
            use_digits=False,
            use_special=False
        )
        self.assertEqual(len(password), 12)
        self.assertTrue(all(c.islower() for c in password))
        self.assertTrue(any(c in self.generator.LOWERCASE for c in password))

    def test_digits_only(self):
        """Test password with only digits."""
        password = self.generator.generate(
            length=12,
            use_uppercase=False,
            use_lowercase=False,
            use_digits=True,
            use_special=False
        )
        self.assertEqual(len(password), 12)
        self.assertTrue(all(c.isdigit() for c in password))
        self.assertTrue(any(c in self.generator.DIGITS for c in password))

    def test_special_only(self):
        """Test password with only special characters."""
        password = self.generator.generate(
            length=12,
            use_uppercase=False,
            use_lowercase=False,
            use_digits=False,
            use_special=True
        )
        self.assertEqual(len(password), 12)
        self.assertTrue(all(c in self.generator.SPECIAL for c in password))

    def test_all_categories_combined(self):
        """Test password contains characters from all selected categories."""
        password = self.generator.generate(
            length=20,
            use_uppercase=True,
            use_lowercase=True,
            use_digits=True,
            use_special=True
        )
        self.assertEqual(len(password), 20)

        # Check that at least one character from each category is present
        has_uppercase = any(c in self.generator.UPPERCASE for c in password)
        has_lowercase = any(c in self.generator.LOWERCASE for c in password)
        has_digit = any(c in self.generator.DIGITS for c in password)
        has_special = any(c in self.generator.SPECIAL for c in password)

        self.assertTrue(has_uppercase, "Password missing uppercase character")
        self.assertTrue(has_lowercase, "Password missing lowercase character")
        self.assertTrue(has_digit, "Password missing digit")
        self.assertTrue(has_special, "Password missing special character")

    def test_multiple_category_combinations(self):
        """Test various combinations of character categories."""
        combinations = [
            (True, True, False, False),   # Upper + lower
            (True, False, True, False),   # Upper + digits
            (True, False, False, True),   # Upper + special
            (False, True, True, False),   # Lower + digits
            (False, True, False, True),   # Lower + special
            (False, False, True, True),   # Digits + special
            (True, True, True, False),    # Upper + lower + digits
            (True, True, False, True),    # Upper + lower + special
        ]

        for upper, lower, digits, special in combinations:
            with self.subTest(upper=upper, lower=lower, digits=digits, special=special):
                password = self.generator.generate(
                    length=16,
                    use_uppercase=upper,
                    use_lowercase=lower,
                    use_digits=digits,
                    use_special=special
                )
                self.assertEqual(len(password), 16)

                # Verify at least one character from each selected category
                if upper:
                    self.assertTrue(any(c in self.generator.UPPERCASE for c in password))
                if lower:
                    self.assertTrue(any(c in self.generator.LOWERCASE for c in password))
                if digits:
                    self.assertTrue(any(c in self.generator.DIGITS for c in password))
                if special:
                    self.assertTrue(any(c in self.generator.SPECIAL for c in password))

    def test_no_categories_selected(self):
        """Test that selecting no categories raises error."""
        with self.assertRaises(NoCharactersSelectedError):
            self.generator.generate(
                length=12,
                use_uppercase=False,
                use_lowercase=False,
                use_digits=False,
                use_special=False
            )

    def test_exclude_ambiguous_characters(self):
        """Test that ambiguous characters are excluded when requested."""
        # Generate many passwords to ensure ambiguous chars don't appear
        for _ in range(10):
            password = self.generator.generate(
                length=20,
                use_uppercase=True,
                use_lowercase=True,
                use_digits=True,
                use_special=False,
                exclude_ambiguous=True
            )

            # Check no ambiguous characters present
            for ambiguous_char in self.generator.AMBIGUOUS:
                self.assertNotIn(
                    ambiguous_char,
                    password,
                    f"Found ambiguous character '{ambiguous_char}' in password"
                )

    def test_ambiguous_exclusion_with_all_categories(self):
        """Test ambiguous character exclusion with all categories enabled."""
        password = self.generator.generate(
            length=24,
            use_uppercase=True,
            use_lowercase=True,
            use_digits=True,
            use_special=True,
            exclude_ambiguous=True
        )

        self.assertEqual(len(password), 24)

        # Verify no ambiguous characters
        for ambiguous_char in self.generator.AMBIGUOUS:
            self.assertNotIn(ambiguous_char, password)

        # Verify at least one from each category (excluding ambiguous)
        # Upper without O
        has_upper = any(c in self.generator.UPPERCASE and c != 'O' for c in password)
        # Lower without l
        has_lower = any(c in self.generator.LOWERCASE and c != 'l' for c in password)
        # Digits without 0 and 1
        has_digit = any(c in self.generator.DIGITS and c not in '01' for c in password)
        # Special chars (no ambiguous)
        has_special = any(c in self.generator.SPECIAL for c in password)

        self.assertTrue(has_upper or has_lower)  # At least one letter
        self.assertTrue(has_digit)
        self.assertTrue(has_special)

    def test_password_length_never_exceeds_requested(self):
        """Test that generated password never exceeds requested length."""
        for length in range(8, 33):
            password = self.generator.generate(length=length)
            self.assertLessEqual(
                len(password),
                length,
                f"Password length {len(password)} exceeds requested {length}"
            )
            self.assertEqual(
                len(password),
                length,
                f"Password length {len(password)} doesn't match requested {length}"
            )

    def test_password_uniqueness(self):
        """Test that multiple generations produce different passwords."""
        passwords = set()
        for _ in range(20):
            password = self.generator.generate(length=16)
            passwords.add(password)

        # With secure randomness, duplicates are astronomically unlikely
        self.assertEqual(len(passwords), 20, "Generated duplicate passwords")

    def test_strength_estimate_weak(self):
        """Test strength estimation for weak passwords."""
        strength = self.generator.estimate_strength(
            "abcd",
            use_uppercase=False,
            use_lowercase=True,
            use_digits=False,
            use_special=False
        )

        self.assertEqual(strength['level'], 'Weak')
        self.assertLess(strength['score'], 40)
        self.assertIn('feedback', strength)

    def test_strength_estimate_fair(self):
        """Test strength estimation for fair passwords."""
        strength = self.generator.estimate_strength(
            "abcd1234",
            use_uppercase=False,
            use_lowercase=True,
            use_digits=True,
            use_special=False
        )

        self.assertIn(strength['level'], ['Fair', 'Weak'])
        self.assertIn('feedback', strength)

    def test_strength_estimate_strong(self):
        """Test strength estimation for strong passwords."""
        strength = self.generator.estimate_strength(
            "Abcd1234!@#$",
            use_uppercase=True,
            use_lowercase=True,
            use_digits=True,
            use_special=True
        )

        self.assertIn(strength['level'], ['Very Strong', 'Strong', 'Fair'])
        self.assertGreaterEqual(strength['score'], 40)
        self.assertIn('feedback', strength)

    def test_strength_estimate_very_strong(self):
        """Test strength estimation for very strong passwords."""
        strength = self.generator.estimate_strength(
            "Abcd1234!@#$XYZ9876",
            use_uppercase=True,
            use_lowercase=True,
            use_digits=True,
            use_special=True
        )

        self.assertIn(strength['level'], ['Very Strong', 'Strong'])
        self.assertGreaterEqual(strength['score'], 60)
        self.assertIn('feedback', strength)

    def test_strength_score_increases_with_length(self):
        """Test that strength score increases with password length."""
        score_8 = self.generator.estimate_strength(
            "A" * 8, True, False, False, False
        )['score']

        score_16 = self.generator.estimate_strength(
            "A" * 16, True, False, False, False
        )['score']

        score_24 = self.generator.estimate_strength(
            "A" * 24, True, False, False, False
        )['score']

        self.assertLess(score_8, score_16)
        self.assertLess(score_16, score_24)

    def test_strength_score_increases_with_diversity(self):
        """Test that strength score increases with character diversity."""
        pwd = "abcdefgh"

        score_1cat = self.generator.estimate_strength(
            pwd, False, True, False, False
        )['score']

        score_2cat = self.generator.estimate_strength(
            pwd, True, True, False, False
        )['score']

        score_3cat = self.generator.estimate_strength(
            pwd, True, True, True, False
        )['score']

        score_4cat = self.generator.estimate_strength(
            pwd, True, True, True, True
        )['score']

        self.assertLess(score_1cat, score_2cat)
        self.assertLess(score_2cat, score_3cat)
        self.assertLess(score_3cat, score_4cat)

    def test_character_pool_size_all_categories(self):
        """Test character pool size calculation with all categories."""
        pool_size = PasswordGenerator.get_character_pool_size(
            use_uppercase=True,
            use_lowercase=True,
            use_digits=True,
            use_special=True,
            exclude_ambiguous=False
        )

        expected = len(set(
            PasswordGenerator.UPPERCASE +
            PasswordGenerator.LOWERCASE +
            PasswordGenerator.DIGITS +
            PasswordGenerator.SPECIAL
        ))

        self.assertEqual(pool_size, expected)

    def test_character_pool_size_with_ambiguous_exclusion(self):
        """Test character pool size when excluding ambiguous characters."""
        pool_size_without = PasswordGenerator.get_character_pool_size(
            use_uppercase=True,
            use_lowercase=True,
            use_digits=True,
            use_special=True,
            exclude_ambiguous=False
        )

        pool_size_with = PasswordGenerator.get_character_pool_size(
            use_uppercase=True,
            use_lowercase=True,
            use_digits=True,
            use_special=True,
            exclude_ambiguous=True
        )

        # Pool should be smaller when excluding ambiguous characters
        self.assertLess(pool_size_with, pool_size_without)

        # Should exclude O, 0, l, 1 (4 characters)
        # But special chars have no ambiguous, so difference depends on overlap
        self.assertGreater(pool_size_without - pool_size_with, 0)

    def test_impossible_character_combination(self):
        """Test error when password length is less than required categories."""
        # Requesting 4 categories but only 2 character slots
        # This should raise an error since we can't guarantee one from each
        with self.assertRaises(PasswordGeneratorError):
            self.generator.generate(
                length=2,
                use_uppercase=True,
                use_lowercase=True,
                use_digits=True,
                use_special=True
            )

    def test_minimum_length_satisfies_categories(self):
        """Test that minimum length can satisfy all category requirements."""
        # With 8 minimum and 4 categories, this should work
        password = self.generator.generate(
            length=8,
            use_uppercase=True,
            use_lowercase=True,
            use_digits=True,
            use_special=True
        )

        self.assertEqual(len(password), 8)

        # Verify all categories represented
        has_uppercase = any(c in self.generator.UPPERCASE for c in password)
        has_lowercase = any(c in self.generator.LOWERCASE for c in password)
        has_digit = any(c in self.generator.DIGITS for c in password)
        has_special = any(c in self.generator.SPECIAL for c in password)

        self.assertTrue(has_uppercase)
        self.assertTrue(has_lowercase)
        self.assertTrue(has_digit)
        self.assertTrue(has_special)


class TestPasswordGeneratorEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = PasswordGenerator()

    def test_exact_minimum_length(self):
        """Test generation at exact minimum boundary."""
        password = self.generator.generate(length=PasswordGenerator.MIN_LENGTH)
        self.assertEqual(len(password), PasswordGenerator.MIN_LENGTH)

    def test_exact_maximum_length(self):
        """Test generation at exact maximum boundary."""
        password = self.generator.generate(length=PasswordGenerator.MAX_LENGTH)
        self.assertEqual(len(password), PasswordGenerator.MAX_LENGTH)

    def test_boundary_minus_one(self):
        """Test just below minimum boundary."""
        with self.assertRaises(InvalidLengthError):
            self.generator.generate(length=PasswordGenerator.MIN_LENGTH - 1)

    def test_boundary_plus_one(self):
        """Test just above maximum boundary."""
        with self.assertRaises(InvalidLengthError):
            self.generator.generate(length=PasswordGenerator.MAX_LENGTH + 1)

    def test_float_length(self):
        """Test that float length is rejected."""
        with self.assertRaises(InvalidLengthError):
            self.generator.generate(length=12.5)

    def test_none_length(self):
        """Test that None length is rejected."""
        with self.assertRaises(InvalidLengthError):
            self.generator.generate(length=None)


if __name__ == '__main__':
    unittest.main(verbosity=2)
