"""
Random Password Generator - Core Logic

This module provides secure password generation using Python's secrets module.
It supports customizable password length, character categories, and strength estimation.
"""

import secrets
import string
from typing import Set, Dict, List


class PasswordGeneratorError(Exception):
    """Base exception for password generator errors."""
    pass


class InvalidLengthError(PasswordGeneratorError):
    """Raised when password length is invalid."""
    pass


class NoCharactersSelectedError(PasswordGeneratorError):
    """Raised when no character categories are selected."""
    pass


class PasswordGenerator:
    """Secure password generator with customizable options."""

    MIN_LENGTH = 8
    MAX_LENGTH = 128

    # Character sets
    UPPERCASE = string.ascii_uppercase
    LOWERCASE = string.ascii_lowercase
    DIGITS = string.digits
    SPECIAL = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # Ambiguous characters that can be confused
    AMBIGUOUS = "O0l1"

    def __init__(self):
        """Initialize the password generator."""
        pass

    def generate(
        self,
        length: int,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_special: bool = True,
        exclude_ambiguous: bool = False
    ) -> str:
        """
        Generate a secure random password.

        Args:
            length: Desired password length (8-128)
            use_uppercase: Include uppercase letters
            use_lowercase: Include lowercase letters
            use_digits: Include digits
            use_special: Include special characters
            exclude_ambiguous: Exclude ambiguous characters (O, 0, l, 1)

        Returns:
            Generated password string

        Raises:
            InvalidLengthError: If length is outside valid range
            NoCharactersSelectedError: If no character categories are selected
        """
        # Validate length
        if not isinstance(length, int) or length < self.MIN_LENGTH or length > self.MAX_LENGTH:
            raise InvalidLengthError(
                f"Password length must be between {self.MIN_LENGTH} and {self.MAX_LENGTH} characters"
            )

        # Build character pool
        char_pool = ""
        required_chars = []

        if use_uppercase:
            chars = self.UPPERCASE
            if exclude_ambiguous:
                chars = "".join(c for c in chars if c not in self.AMBIGUOUS)
            if chars:
                char_pool += chars
                required_chars.append(secrets.choice(chars))

        if use_lowercase:
            chars = self.LOWERCASE
            if exclude_ambiguous:
                chars = "".join(c for c in chars if c not in self.AMBIGUOUS)
            if chars:
                char_pool += chars
                required_chars.append(secrets.choice(chars))

        if use_digits:
            chars = self.DIGITS
            if exclude_ambiguous:
                chars = "".join(c for c in chars if c not in self.AMBIGUOUS)
            if chars:
                char_pool += chars
                required_chars.append(secrets.choice(chars))

        if use_special:
            chars = self.SPECIAL
            if exclude_ambiguous:
                chars = "".join(c for c in chars if c not in self.AMBIGUOUS)
            if chars:
                char_pool += chars
                required_chars.append(secrets.choice(chars))

        # Validate character pool
        if not char_pool:
            raise NoCharactersSelectedError(
                "No characters available. Please select at least one character category."
            )

        # Check if requested length can accommodate required characters
        if len(required_chars) > length:
            raise PasswordGeneratorError(
                f"Cannot generate password: need at least {len(required_chars)} characters "
                f"to satisfy category requirements, but length is {length}"
            )

        # Generate password ensuring each selected category is represented
        password_chars = required_chars.copy()

        # Fill remaining positions with random characters from the pool
        remaining_length = length - len(required_chars)
        password_chars.extend(secrets.choice(char_pool) for _ in range(remaining_length))

        # Securely shuffle the password characters
        # Using secrets.SystemRandom for cryptographically secure shuffling
        rng = secrets.SystemRandom()
        rng.shuffle(password_chars)

        return "".join(password_chars)

    def estimate_strength(
        self,
        password: str,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_special: bool = True
    ) -> Dict[str, any]:
        """
        Estimate password strength based on length and character diversity.

        This is a heuristic estimate, not a guarantee of security.

        Args:
            password: Password to evaluate
            use_uppercase: Whether uppercase was included
            use_lowercase: Whether lowercase was included
            use_digits: Whether digits were included
            use_special: Whether special characters were included

        Returns:
            Dictionary with 'level' (str), 'score' (int 0-100), and 'feedback' (str)
        """
        length = len(password)

        # Count character categories used
        categories_used = sum([use_uppercase, use_lowercase, use_digits, use_special])

        # Calculate base score from length
        if length < 8:
            length_score = 0
        elif length < 12:
            length_score = 25
        elif length < 16:
            length_score = 40
        elif length < 20:
            length_score = 50
        else:
            length_score = 60

        # Add score for character diversity
        diversity_score = categories_used * 10

        # Total score
        score = min(100, length_score + diversity_score)

        # Determine strength level and feedback
        if score < 40:
            level = "Weak"
            feedback = "Consider using a longer password with more character types"
        elif score < 60:
            level = "Fair"
            feedback = "Acceptable but could be stronger with more length or diversity"
        elif score < 80:
            level = "Strong"
            feedback = "Good password with decent length and character diversity"
        else:
            level = "Very Strong"
            feedback = "Excellent password with high length and character diversity"

        return {
            "level": level,
            "score": score,
            "feedback": feedback
        }

    @staticmethod
    def get_character_pool_size(
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_special: bool = True,
        exclude_ambiguous: bool = False
    ) -> int:
        """
        Calculate the size of the character pool based on selections.

        Returns:
            Total number of unique characters available
        """
        pool: Set[str] = set()

        if use_uppercase:
            chars = PasswordGenerator.UPPERCASE
            if exclude_ambiguous:
                chars = "".join(c for c in chars if c not in PasswordGenerator.AMBIGUOUS)
            pool.update(chars)

        if use_lowercase:
            chars = PasswordGenerator.LOWERCASE
            if exclude_ambiguous:
                chars = "".join(c for c in chars if c not in PasswordGenerator.AMBIGUOUS)
            pool.update(chars)

        if use_digits:
            chars = PasswordGenerator.DIGITS
            if exclude_ambiguous:
                chars = "".join(c for c in chars if c not in PasswordGenerator.AMBIGUOUS)
            pool.update(chars)

        if use_special:
            pool.update(PasswordGenerator.SPECIAL)

        return len(pool)


if __name__ == "__main__":
    # Example usage
    generator = PasswordGenerator()

    try:
        password = generator.generate(
            length=16,
            use_uppercase=True,
            use_lowercase=True,
            use_digits=True,
            use_special=True,
            exclude_ambiguous=False
        )
        print(f"Generated password: {password}")

        strength = generator.estimate_strength(
            password,
            use_uppercase=True,
            use_lowercase=True,
            use_digits=True,
            use_special=True
        )
        print(f"Strength: {strength['level']} (Score: {strength['score']})")
        print(f"Feedback: {strength['feedback']}")

    except PasswordGeneratorError as e:
        print(f"Error: {e}")
