# OIBSIP — Quick Launch Commands

Run any task directly from the repository root. All tasks are **desktop Tkinter applications** — no web server, no localhost, no browser required.

---

## Prerequisites
```powershell
# One-time setup (run once)
cd C:\Users\bharath\OneDrive\Desktop\OIBSIP

# Task 2 & 4 need external packages
pip install -r Python-Task2-BMICalculator/requirements.txt
pip install -r Python-Task4-WeatherApp/requirements.txt
```

---

## Individual Task Launch

### Task 1 — NOVA Voice Assistant
```powershell
cd C:\Users\bharath\OneDrive\Desktop\OIBSIP
python Python-Task1-VoiceAssistant/app.py
```
- **Theme**: Charcoal/Navy with Electric Blue/Violet accents
- **Features**: 5-ring animated voice orb, speech recognition (PyAudio), TTS (pyttsx3), thread-safe queue architecture

### Task 2 — BMI Calculator
```powershell
cd C:\Users\bharath\OneDrive\Desktop\OIBSIP
python Python-Task2-BMICalculator/bmi_calculator.py
```
- **Theme**: Dark graphite with Emerald/Teal accents
- **Features**: Multi-user SQLite, matplotlib trend charts, WHO categories, color-coded results
- **Requires**: `pip install matplotlib numpy` (in requirements.txt)

### Task 3 — Password Generator
```powershell
cd C:\Users\bharath\OneDrive\Desktop\OIBSIP
python Python-Task3-PasswordGenerator/app.py
```
- **Theme**: Dark purple/indigo with Violet/Teal accents
- **Features**: `secrets` module crypto RNG, strength meter, category guarantees, clipboard copy
- **No external deps** — pure stdlib

### Task 4 — Weather Dashboard
```powershell
cd C:\Users\bharath\OneDrive\Desktop\OIBSIP
python Python-Task4-WeatherApp/app.py
```
- **Theme**: Dark purple with Lavender accents
- **Features**: Open-Meteo API (no key), current + 24h hourly strip + 7-day cards, °C/°F toggle, horizontal scrolling
- **Requires**: `pip install requests` (in requirements.txt)

---

## VS Code Launch (Recommended)

Press **F5** in VS Code → select **"Launch All 4 Tasks"** from the dropdown → all four apps start simultaneously in debug terminals.

Or run individually:
1. Open **Run and Debug** panel (Ctrl+Shift+D)
2. Select any single task from dropdown
3. Press **F5**

---

## Test Commands

Run all test suites from repo root:
```powershell
# Task 1 (26 tests)
python -m unittest Python-Task1-VoiceAssistant.tests.test_app -v

# Task 2 (32 tests)
python -m unittest Python-Task2-BMICalculator.tests.test_bmi -v

# Task 3 (35 tests)
python -m unittest Python-Task3-PasswordGenerator.tests.test_password_generator -v

# Task 4 (31 tests)
python -m unittest Python-Task4-WeatherApp.tests.test_weather_service -v
```

**Total: 124 tests — all passing.**

---

## Screenshots Location
After manual capture (Win+Shift+S), save to:
- `Python-Task1-VoiceAssistant/screenshots/`
- `Python-Task2-BMICalculator/screenshots/`
- `Python-Task3-PasswordGenerator/screenshots/`  ← already has 3 images
- `Python-Task4-WeatherApp/screenshots/`  ← already has 4 images

---

## Notes
- **Task 5 (ChatApplication)** is intentionally excluded from submission
- **PyAudio wheel** (`PyAudio-0.2.14-cp313-cp313-win_amd64.whl`) is excluded from git
- **SQLite DB files** (`bmi_history.db`, `chat.db`) are in `.gitignore`
- All apps use `threading` + `root.after()` for thread-safe GUI updates
- All apps are **responsive** — resize windows freely

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: matplotlib` | `pip install -r Python-Task2-BMICalculator/requirements.txt` |
| `ModuleNotFoundError: requests` | `pip install -r Python-Task4-WeatherApp/requirements.txt` |
| `ImportError: pyaudio` | Task 1 only — install `PyAudio-0.2.14-cp313-cp313-win_amd64.whl` from Task 1 folder |
| Tkinter not found (Linux) | `sudo apt-get install python3-tk` |
| Port 8080 error | Irrelevant — these are desktop apps, not web servers |