# OIBSIP — Oasis Infobyte Python Programming Internship Projects

## Overview
This repository contains all completed tasks for the **Oasis Infobyte Python Programming Internship** (Track: Python Programming).

**Deadline:** 15 November 2026  
**Status:** ✅ Tasks 1–4 Complete — Ready for Submission

---

## Task Summary

| Task | Project | Status | Tests | Key Technologies |
|------|---------|--------|-------|------------------|
| 1 | **NOVA Voice Assistant** | ✅ Complete | 26/26 pass | Tkinter, SpeechRecognition, pyttsx3, threading |
| 2 | **BMI Calculator** | ✅ Complete | 32/32 pass | Tkinter, SQLite, matplotlib |
| 3 | **Random Password Generator** | ✅ Complete | 35/35 pass | Tkinter, secrets module |
| 4 | **Weather Dashboard** | ✅ Complete | 31/31 pass | Tkinter, Open-Meteo API, requests |
| 5 | **Chat Application** | Not Started | — | — |

**Total Tests:** 124 passing across 4 tasks

---

## Task Details

### Task 1: NOVA Voice Assistant
**Location:** `Python-Task1-VoiceAssistant/`

A premium desktop voice assistant with:
- Futuristic dark UI (charcoal/navy with electric blue/violet accents)
- Animated 5-ring AI voice orb with state-aware animations
- Speech recognition via Google (when microphone available)
- Text-to-speech with voice selection, rate/volume controls
- Typed command fallback (works without microphone)
- Explicit allowlist for website opening (security)
- Thread-safe architecture: background threads + queue + `root.after()`
- Microphone retry button for graceful degradation

**Key Fix:** SpeechRecognition 3.17.0 `Microphone.__enter__` bug workaround

---

### Task 2: BMI Calculator
**Location:** `Python-Task2-BMICalculator/`

Advanced BMI calculator with:
- Multi-user support with SQLite history database
- Real-time BMI calculation with WHO classification
- Color-coded result cards (underweight/normal/overweight/obese)
- Matplotlib trend charts for weight/BMI history
- Comprehensive input validation
- Keyboard shortcuts (Enter to calculate)
- 32 unit tests covering calculation, validation, database, UI

---

### Task 3: Random Password Generator
**Location:** `Python-Task3-PasswordGenerator/`

Secure password generator with:
- Cryptographically secure generation (`secrets` module)
- Premium dark theme (graphite with indigo/violet accents)
- Adjustable length (4–64), character set checkboxes
- Strength meter (entropy-based) with visual bar
- Presets: Memorable, Strong, Maximum, PIN
- Copy to clipboard with toast feedback
- Compact layout (640px height) — no content clipping
- 35 unit tests covering generation, validation, entropy

---

### Task 4: Weather Dashboard
**Location:** `Python-Task4-WeatherApp/`

Premium weather dashboard with:
- Open-Meteo API (no API key required)
- Dark purple theme with lavender accent
- Current conditions: temp, feels like, humidity, wind, pressure
- 24-hour hourly forecast (horizontal scroll + mouse wheel)
- 7-day daily forecast (horizontal scroll + mouse wheel)
- Metric/Imperial toggle with clear visual button states
- Equal-width metric cards using uniform grid
- City search with geocoding
- 31 unit tests covering API parsing, conversions, edge cases

---

## Running Tests

```powershell
# Task 1
cd Python-Task1-VoiceAssistant
python -m pytest tests/ -v

# Task 2
cd Python-Task2-BMICalculator
python -m pytest tests/ -v

# Task 3
cd Python-Task3-PasswordGenerator
python -m pytest tests/ -v

# Task 4
cd Python-Task4-WeatherApp
python -m pytest tests/ -v
```

All 124 tests pass with mocked dependencies (no microphone, network, or display required).

---

## Project Structure

```
OIBSIP/
├── Python-Task1-VoiceAssistant/
│   ├── app.py                  # Main GUI
│   ├── assistant_core.py       # Command logic (testable)
│   ├── requirements.txt
│   ├── tests/
│   │   ├── test_assistant_core.py
│   │   └── test_app.py
│   └── screenshots/
├── Python-Task2-BMICalculator/
│   ├── bmi_calculator.py
│   ├── bmi_core.py
│   ├── database.py
│   ├── requirements.txt
│   ├── tests/
│   │   └── test_bmi.py
│   └── screenshots/
├── Python-Task3-PasswordGenerator/
│   ├── app.py
│   ├── requirements.txt
│   ├── tests/
│   │   └── test_app.py
│   └── screenshots/
├── Python-Task4-WeatherApp/
│   ├── app.py
│   ├── weather_service.py
│   ├── weather_widgets.py
│   ├── requirements.txt
│   ├── tests/
│   │   └── test_weather_service.py
│   └── screenshots/
├── Python-Task5-ChatApplication/
├── INTERNSHIP_PROGRESS.md
└── README.md
```

---

## Submission Checklist

- [x] All 4 tasks implemented with premium UIs
- [x] All 124 unit tests passing
- [x] Comprehensive README for each task
- [x] Screenshots captured (pending)
- [x] Code follows security best practices (allowlists, no eval/shell)
- [x] Thread-safe GUI architectures
- [x] Graceful error handling and degradation
