# Random Password Generator

A secure desktop application for generating random passwords with customizable options and strength feedback.

Built for **Oasis Infobyte Python Programming Internship - Task 3**.

---

## Features

✅ **Secure Generation**: Uses Python's `secrets` module for cryptographically secure randomness  
✅ **Customizable Length**: Generate passwords from 8 to 128 characters  
✅ **Character Categories**: Choose from uppercase, lowercase, digits, and special characters  
✅ **Ambiguous Character Exclusion**: Option to exclude easily confused characters (O, 0, l, 1)  
✅ **Strength Estimation**: Real-time password strength feedback with explanatory messages  
✅ **User-Friendly GUI**: Clean Tkinter interface with keyboard shortcuts  
✅ **Clipboard Integration**: One-click copy to clipboard  
✅ **Category Guarantee**: Ensures at least one character from each selected category  
✅ **Comprehensive Testing**: Full unit test suite with 35+ test cases

---

## Project Structure

```
Python-Task3-PasswordGenerator/
│
├── password_generator.py        # Core password generation logic
├── app.py                       # Tkinter GUI application
├── tests/
│   └── test_password_generator.py  # Unit tests
├── screenshots/                 # Application screenshots (after manual capture)
├── README.md                    # This file
├── requirements.txt             # External dependencies (minimal)
└── .gitignore                   # Git exclusions
```

---

## Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows, macOS, or Linux
- **Dependencies**: None (uses Python standard library only)

### Standard Library Modules Used
- `secrets` - Cryptographically secure random generation
- `string` - Character set constants
- `tkinter` - GUI framework
- `unittest` - Testing framework

---

## Installation and Setup

### 1. Prerequisites

Ensure Python 3.7+ is installed:
```bash
python --version
```

### 2. Clone or Download the Repository

Navigate to the OIBSIP repository:
```bash
cd C:\Users\bharath\OneDrive\Desktop\OIBSIP
```

### 3. Navigate to Task 3 Folder

```bash
cd Python-Task3-PasswordGenerator
```

### 4. (Optional) Create a Virtual Environment

**Windows (PowerShell/CMD):**
```bash
python -m venv venv
venv\Scripts\activate
```

**Windows (Git Bash):**
```bash
python -m venv venv
source venv/Scripts/activate
```

**Note**: A virtual environment is optional for this project since it has no external dependencies.

---

## Usage

### Running the Application

**From VS Code Terminal (Git Bash):**
```bash
python app.py
```

**Or directly:**
```bash
cd C:\Users\bharath\OneDrive\Desktop\OIBSIP\Python-Task3-PasswordGenerator
python app.py
```

### Using the GUI

1. **Set Password Length**: Enter a number between 8 and 128
2. **Select Character Categories**: Check the boxes for the types of characters you want
3. **Options**: Optionally exclude ambiguous characters (O, 0, l, 1)
4. **Generate**: Click "Generate Password" or press Enter
5. **Copy**: Click "Copy to Clipboard" or press Ctrl+C
6. **Clear**: Click "Clear" to remove the password from display

### Keyboard Shortcuts

- **Enter** or **Ctrl+G**: Generate password
- **Ctrl+C**: Copy to clipboard

---

## Running Tests

### Run All Tests

```bash
python -m unittest tests.test_password_generator -v
```

### Run Specific Test Class

```bash
python -m unittest tests.test_password_generator.TestPasswordGenerator -v
```

### Run a Single Test

```bash
python -m unittest tests.test_password_generator.TestPasswordGenerator.test_all_categories_combined -v
```

### Expected Output

```
test_all_categories_combined ... ok
test_ambiguous_exclusion_with_all_categories ... ok
...
----------------------------------------------------------------------
Ran 35 tests in 0.XXXs

OK
```

---

## Security Considerations

### What This Application Does

✅ Uses `secrets` module for cryptographically secure randomness  
✅ Guarantees at least one character from each selected category  
✅ Validates all inputs before generation  
✅ Does not log or persist generated passwords  
✅ Clears passwords from display when requested  
✅ Provides strength estimates to guide password selection  

### Limitations and Best Practices

⚠️ **Clipboard Security**: After copying, the password remains in your clipboard and may be accessible to other applications. Clear your clipboard after use.

⚠️ **Strength Estimate**: The strength indicator is a heuristic estimate based on length and character diversity. It is NOT a guarantee of security.

⚠️ **No Password Storage**: This application does not store passwords. Use a dedicated password manager to securely store your generated passwords.

⚠️ **Display Security**: Generated passwords are displayed in plain text. Ensure your screen is not visible to others when generating passwords.

⚠️ **Random Number Generator**: While `secrets` is cryptographically secure, the security of generated passwords also depends on your system's entropy source.

### Recommended Usage

1. Generate passwords of at least 12-16 characters
2. Use all character categories for maximum entropy
3. Store generated passwords in a reputable password manager
4. Don't reuse passwords across different accounts
5. Consider excluding ambiguous characters for passwords you'll type frequently

---

## Testing Coverage

The test suite covers:

- ✅ Minimum, typical, and maximum password lengths
- ✅ All character category combinations
- ✅ Ambiguous character exclusion
- ✅ Invalid inputs (wrong types, out-of-range values)
- ✅ Edge cases (boundary values, impossible combinations)
- ✅ Strength estimation accuracy
- ✅ Password uniqueness and randomness
- ✅ Category representation guarantees

**Total Tests**: 35  
**Test Classes**: 2

---

## Capturing Screenshots

To capture screenshots for your internship submission:

### Windows

1. **Run the Application**: `python app.py`
2. **Open Snipping Tool**: Press `Windows + Shift + S`
3. **Select Area**: Click and drag to select the application window
4. **Save**: The screenshot is copied to clipboard - paste it into an image editor and save to `screenshots/` folder

### Recommended Screenshots

1. **Main Interface**: Show the application with all options visible
2. **Generated Password**: Show a generated password with strength indicator
3. **Different Character Options**: Show various category selections
4. **Success Message**: Show the success dialog after generation
5. **Copy Confirmation**: Show the clipboard copy confirmation

---

## Development Notes

### File Organization

- **password_generator.py**: Contains the `PasswordGenerator` class with all core logic separated from the GUI
- **app.py**: Tkinter GUI that imports and uses the `PasswordGenerator` class
- **tests/test_password_generator.py**: Comprehensive unit tests for core logic only (no GUI testing)

### Design Decisions

1. **Separation of Concerns**: Core logic is independent of GUI for testability
2. **Security First**: Uses `secrets` module instead of `random` for password generation
3. **Category Guarantees**: Ensures representation by pre-selecting one character from each category
4. **User Feedback**: Clear error messages and strength estimates guide users
5. **No Dependencies**: Uses only standard library to minimize setup complexity

---

## Troubleshooting

### Issue: "python: command not found"

**Solution**: Ensure Python is installed and added to PATH. Try `python3` instead of `python`.

### Issue: Tkinter Import Error

**Solution**: Tkinter is included with Python on Windows and macOS. On Linux, install:
```bash
sudo apt-get install python3-tk
```

### Issue: Tests Fail with ModuleNotFoundError

**Solution**: Ensure you're running tests from the `Python-Task3-PasswordGenerator` directory:
```bash
cd Python-Task3-PasswordGenerator
python -m unittest tests.test_password_generator -v
```

### Issue: Generated Password Shows Ambiguous Characters Despite Exclusion

**Solution**: This is a bug. Report it! The tests verify exclusion works correctly, so check if you're testing with the right options enabled.

---

## Internship Information

**Internship**: Oasis Infobyte Python Programming  
**Task**: Task 3 - Random Password Generator  
**Completed**: October 2026  
**Repository**: `OIBSIP`

### Previous Tasks

- ✅ **Task 2**: BMI Calculator (located in `Python-Task2-BMICalculator/`)

---

## License

This project is created as part of the Oasis Infobyte internship program for educational purposes.

---

## Author

**A. Vagadhish**  
Oasis Infobyte Python Programming Intern

---

## Acknowledgments

- **Oasis Infobyte** for the internship opportunity
- Python's `secrets` module documentation for security guidance
- Tkinter documentation for GUI development patterns
