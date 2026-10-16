# BMI Calculator - Advanced Desktop Application

**Oasis Infobyte Python Programming Internship - Task 2**

A comprehensive desktop application for calculating and tracking Body Mass Index (BMI) with user history and trend visualization.

---

## 📋 Project Overview

This BMI Calculator is an advanced desktop GUI application built with Python and tkinter. It allows users to calculate their BMI, save historical records, view past calculations, and visualize BMI trends over time using interactive charts.

### Problem Statement

Body Mass Index (BMI) is a widely used screening measure for weight categories. This application makes it easy for users to:
- Calculate their BMI quickly and accurately
- Track BMI changes over time
- Visualize trends through interactive charts
- Maintain separate records for multiple users

---

## ✨ Features Implemented

### Beginner Tier (Required)
✅ Accept weight in kilograms and height in metres  
✅ Calculate BMI using the formula: BMI = weight / height²  
✅ Classify results into WHO categories:
  - Underweight: BMI < 18.5
  - Normal: BMI 18.5–24.9
  - Overweight: BMI 25–29.9
  - Obese: BMI ≥ 30  
✅ Display BMI rounded to two decimal places  
✅ Validate all inputs with helpful error messages  
✅ GUI with labelled input fields and Calculate button  

### Advanced Tier (Implemented)
✅ Color-coded BMI results for visual clarity  
✅ Multiple named user support  
✅ Persistent SQLite database for historical records  
✅ View complete BMI history for each user  
✅ Interactive matplotlib trend charts  
✅ Polished, accessible, responsive interface  
✅ BMI disclaimer for medical guidance  
✅ Keyboard-friendly controls (Enter key support)  
✅ User selection from dropdown of existing users  

---

## 🛠 Technology Stack

- **Language**: Python 3.13.14
- **GUI Framework**: tkinter (built-in)
- **Database**: SQLite3 (built-in)
- **Data Visualization**: matplotlib 3.8+
- **Testing**: unittest (built-in)

---

## 📁 Project Structure

```
Python-Task2-BMICalculator/
├── bmi_calculator.py       # Main GUI application
├── bmi_core.py            # BMI calculation and validation logic
├── database.py            # SQLite database operations
├── requirements.txt       # External dependencies
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── tests/
│   └── test_bmi.py       # Comprehensive unit tests (32 tests)
└── screenshots/
    └── (screenshots to be added)
```

---

## 📦 Prerequisites

- **Python**: Version 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Display**: GUI requires a graphical display environment

---

## 🚀 Setup Instructions (Windows)

### 1. Clone or Download the Repository

```powershell
cd C:\Users\YourName\Desktop
git clone https://github.com/YourUsername/OIBSIP.git
cd OIBSIP\Python-Task2-BMICalculator
```

### 2. Create Virtual Environment

```powershell
python -m venv .venv
```

### 3. Activate Virtual Environment

```powershell
.venv\Scripts\Activate.ps1
```

If you encounter a PowerShell execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- matplotlib (for trend charts)
- numpy (matplotlib dependency)

### 5. Verify Installation

```powershell
python --version
python -c "import tkinter; import matplotlib; print('All dependencies OK')"
```

---

## 🎮 How to Run

### Launch the Application

```powershell
# Make sure virtual environment is activated
.venv\Scripts\Activate.ps1

# Run the application
python bmi_calculator.py
```

The BMI Calculator window will open.

---

## 📖 Usage Instructions

### Calculate Your BMI

1. **Enter Your Name** (optional): Type your name or select an existing user from the dropdown
2. **Enter Weight**: Input your weight in kilograms (e.g., 70)
3. **Enter Height**: Input your height in metres (e.g., 1.75)
4. **Click "Calculate BMI"** or press Enter
5. Your BMI result will appear with color-coded category:
   - 🔵 Blue: Underweight
   - 🟢 Green: Normal
   - 🟠 Orange: Overweight
   - 🔴 Red: Obese

### View Your History

1. Enter or select your name
2. Click **"View History"**
3. A new window shows all your past BMI records with dates

### Show BMI Trend

1. Enter or select your name (must have at least 2 records)
2. Click **"Show Trend"**
3. An interactive chart displays your BMI changes over time with category zones

### Clear Inputs

- Click **"Clear"** to reset all fields and start fresh

---

## 🧪 Testing

### Run Unit Tests

```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Run all tests
python tests\test_bmi.py
```

### Test Coverage

✅ **32 unit tests** covering:
- BMI calculations (4 tests)
- Category classifications (6 tests)
- Input validation (13 tests)
- Category colors (2 tests)
- Database operations (7 tests)

All tests pass successfully.

### Manual Testing Checklist

- [ ] Valid BMI calculation (70 kg, 1.75 m → 22.86, Normal)
- [ ] All category boundaries (18.5, 25.0, 30.0)
- [ ] Empty input fields
- [ ] Non-numeric inputs
- [ ] Negative values
- [ ] Zero height
- [ ] Unrealistic values (600 kg, 5 m)
- [ ] Multiple user records
- [ ] History view
- [ ] Trend chart with 2+ records
- [ ] Keyboard shortcuts (Enter key)
- [ ] Color-coded results

---

## 📸 Screenshots

### Main Application Window
*(Screenshot to be added after running the application)*

### BMI Result Display
*(Screenshot showing calculated BMI with color coding)*

### History View
*(Screenshot of history window with multiple records)*

### Trend Chart
*(Screenshot of matplotlib BMI trend visualization)*

---

## 🎯 Input Validation

The application validates:
- **Empty fields**: Prompts user to enter required values
- **Non-numeric input**: Rejects text and special characters
- **Weight range**: 0 < weight ≤ 500 kg
- **Height range**: 0.5 ≤ height ≤ 3.0 metres
- **Zero values**: Rejects zero for weight and height
- **Negative values**: Rejects negative numbers

All validation errors show friendly, actionable messages.

---

## 🗄 Database

### Database File
- **File**: `bmi_history.db` (created automatically on first run)
- **Type**: SQLite3
- **Location**: Same directory as `bmi_calculator.py`

### Schema

```sql
CREATE TABLE bmi_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    weight REAL NOT NULL,
    height REAL NOT NULL,
    bmi REAL NOT NULL,
    category TEXT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Data Persistence
- Records are saved permanently
- Each user's history is kept separate
- Data survives application restarts
- No manual database management needed

**⚠️ Note**: `bmi_history.db` is excluded from Git via `.gitignore` to protect user privacy.

---

## ⚠️ Known Limitations

1. **Height Input**: Requires height in metres (not cm or feet/inches)
2. **BMI Limitations**: BMI does not account for:
   - Muscle mass
   - Bone density
   - Body composition
   - Age and gender differences
3. **Single Device**: Database is local, not synced across devices
4. **No User Authentication**: Anyone can view any user's history
5. **No Data Export**: History cannot be exported to CSV/Excel (future enhancement)

---

## 🔮 Future Improvements

- [ ] Support for height in cm and feet/inches
- [ ] Imperial units (pounds, feet/inches)
- [ ] Export history to CSV
- [ ] BMI-for-age percentiles (children)
- [ ] Body fat percentage calculator
- [ ] Weekly/monthly average calculations
- [ ] Dark mode toggle
- [ ] User profile pictures
- [ ] Data backup and restore

---

## 🩺 Medical Disclaimer

⚠️ **Important**: BMI is a screening measure and **not a diagnostic tool**. It does not account for muscle mass, bone density, overall body composition, or individual health factors.

**This application does not provide medical advice.** Consult a qualified healthcare professional for:
- Personalized health assessment
- Weight management advice
- Nutrition guidance
- Medical diagnosis

---

## 📚 References

- [WHO BMI Classification](https://www.who.int/europe/news-room/fact-sheets/item/a-healthy-lifestyle---who-recommendations)
- [CDC BMI Information](https://www.cdc.gov/healthyweight/assessing/bmi/index.html)
- [Python tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [Matplotlib Documentation](https://matplotlib.org/stable/index.html)

---

## 🌐 Web Browser Version

In addition to the main Python tkinter application, this project includes a **browser-based version** for demonstration and portfolio purposes.

### Quick Start
```powershell
# Open in Chrome (or any browser)
cd web-version
# Double-click index.html, or:
start chrome index.html
```

### Features
- ✅ Same BMI calculation logic
- ✅ localStorage-based history (browser-local)
- ✅ Responsive design (mobile + desktop)
- ✅ Dark mode support
- ✅ Interactive Chart.js trend visualization
- ✅ No installation required

### Comparison

| Feature | Python (tkinter) | Browser (HTML/JS) |
|---------|------------------|-------------------|
| **Storage** | SQLite database | Browser localStorage |
| **Platform** | Desktop only | Any device with browser |
| **Submission** | ✅ Primary internship submission | Portfolio enhancement |
| **Multi-user** | True database | Browser-local tracking |
| **Offline** | Fully offline | Needs Chart.js CDN once |

**See `web-version/README.md` for complete browser version documentation.**

---

## 👨‍💻 Developer Information

**Project**: Oasis Infobyte Python Programming Internship  
**Task**: Task 2 - BMI Calculator (Advanced)  
**Primary Submission**: Python tkinter desktop application  
**Technology**: Python 3.13, tkinter, SQLite, matplotlib  
**Additional**: Browser-based version (HTML/CSS/JavaScript)  
**Test Coverage**: 32 unit tests, all passing  
**Status**: ✅ Complete and ready for submission

---

## 📄 License

This project is developed as part of the Oasis Infobyte internship program for educational purposes.

---

**Last Updated**: October 13, 2026
