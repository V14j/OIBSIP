"""
BMI Calculator - Core Logic Module
Handles BMI calculation, classification, and input validation.
"""

from typing import Tuple


def calculate_bmi(weight: float, height: float) -> float:
    """
    Calculate BMI using the formula: weight / (height ** 2)

    Args:
        weight: Weight in kilograms
        height: Height in metres

    Returns:
        BMI value rounded to 2 decimal places
    """
    bmi = weight / (height ** 2)
    return round(bmi, 2)


def classify_bmi(bmi: float) -> str:
    """
    Classify BMI into standard WHO categories.

    Args:
        bmi: BMI value

    Returns:
        Category string: "Underweight", "Normal", "Overweight", or "Obese"
    """
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25.0:
        return "Normal"
    elif bmi < 30.0:
        return "Overweight"
    else:
        return "Obese"


def get_category_color(category: str) -> str:
    """
    Get the color code for each BMI category for GUI display.

    Args:
        category: BMI category string

    Returns:
        Color code string for tkinter
    """
    colors = {
        "Underweight": "#3498db",  # Blue
        "Normal": "#2ecc71",       # Green
        "Overweight": "#f39c12",   # Orange
        "Obese": "#e74c3c"         # Red
    }
    return colors.get(category, "#000000")


def validate_input(weight_str: str, height_str: str, username: str = "") -> Tuple[bool, str, float, float]:
    """
    Validate user input for weight, height, and optional username.

    Args:
        weight_str: Weight input as string
        height_str: Height input as string
        username: Optional username (can be empty)

    Returns:
        Tuple of (is_valid, error_message, weight_float, height_float)
        If invalid, weight_float and height_float will be 0.0
    """
    # Check for empty inputs
    if not weight_str.strip():
        return False, "Please enter your weight.", 0.0, 0.0

    if not height_str.strip():
        return False, "Please enter your height.", 0.0, 0.0

    # Try to convert to float
    try:
        weight = float(weight_str.strip())
    except ValueError:
        return False, "Weight must be a valid number.", 0.0, 0.0

    try:
        height = float(height_str.strip())
    except ValueError:
        return False, "Height must be a valid number.", 0.0, 0.0

    # Validate weight range
    if weight <= 0:
        return False, "Weight must be greater than zero.", 0.0, 0.0

    if weight > 500:
        return False, "Please enter a realistic weight (max 500 kg).", 0.0, 0.0

    # Validate height range
    if height <= 0:
        return False, "Height must be greater than zero.", 0.0, 0.0

    if height > 3.0:
        return False, "Please enter height in metres (e.g., 1.75).", 0.0, 0.0

    if height < 0.5:
        return False, "Please enter a realistic height (min 0.5 m).", 0.0, 0.0

    # All validations passed
    return True, "", weight, height
