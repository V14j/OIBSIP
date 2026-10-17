# Advanced Weather Dashboard

Premium desktop weather application with current conditions, 24-hour hourly forecast, 7-day daily forecast, metric cards, weather icons, and responsive design. Built for **Oasis Infobyte Python Programming Internship - Task 4**.

---

## Features (Advanced Tier)

✅ **Real-time Current Weather** — temperature, feels-like, description, humidity, wind, pressure  
✅ **24-Hour Forecast** — scrollable hourly strip with temp, condition icon, precipitation %  
✅ **7-Day Forecast** — daily cards with high/low, weather icon/description  
✅ **No API Key Required** — Open-Meteo free tier  
✅ **Celsius / Fahrenheit Toggle** — consistent conversion across all values  
✅ **Weather Icons** — Unicode symbols mapped to WMO weather codes (clear, cloudy, rain, snow, storm, fog)  
✅ **Background Threading** — UI never freezes during fetches  
✅ **Stale-Result Protection** — older searches can't overwrite newer results  
✅ **Error Handling** — invalid cities, timeouts, network failures, malformed JSON  
✅ **Attribution** — "Weather data by Open-Meteo.com" visible  
✅ **31 Unit Tests** — current + hourly/daily parsing + conversions + errors

---

## Project Structure

```
Python-Task4-WeatherApp/
│
├── app.py                      # Main Tkinter dashboard
├── weather_widgets.py          # Cards, icons, forecast widgets
├── weather_service.py          # Open-Meteo API + parsing
├── tests/
│   └── test_weather_service.py # 31 mocked tests
├── screenshots/                # For internship submission
├── requirements.txt            # requests only
└── README.md                   # This file
```

---

## Requirements

- Python 3.7+
- Windows / macOS / Linux
- Internet connection (for live data)
- `requests` (installed via requirements.txt)
- `tkinter` (included with Python)

---

## Installation (Windows PowerShell)

```powershell
cd C:\Users\bharath\OneDrive\Desktop\OIBSIP\Python-Task4-WeatherApp
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Running the Application

```powershell
python app.py
```

Or with virtual environment:
```powershell
.\venv\Scripts\Activate.ps1
python app.py
```

---

## Usage

1. Type a city (e.g., `London`, `Paris,FR`, `Tokyo`)
2. Click **Search** or press **Enter / Ctrl+R**
3. View current conditions + hourly strip + 7-day cards
4. Click **°C / °F** to switch units (all temperatures convert)
5. Search again — newer results take precedence

---

## Running Tests

```powershell
python -m unittest tests.test_weather_service -v
```

Expected: **31 tests passing** (27 original + 4 new for hourly/daily parsing).

---

## Advanced Features Implemented (Working Specification)

Per the working specification (original internship PDF unavailable for verification):

| Requirement | Status | Evidence |
|---|---|---|
| Open-Meteo (no API key) | ✅ Implemented | `weather_service.py` uses `open-meteo.com` endpoints |
| Current weather (temp, feels-like, desc, humidity, wind, pressure) | ✅ Implemented | `app.py` large display + 4 metric cards |
| Hourly forecast (next 24h) | ✅ Implemented | Horizontal scrollable strip; `_parse_hourly()`; `hourly` API params |
| Daily forecast (5–7 days) | ✅ Implemented | 7-day card row; `_parse_daily()`; `daily` API params |
| Temperature unit toggle (C ↔ F) | ✅ Implemented | `set_units()` converts current + forecasts consistently |
| Weather icons (unicode, mapped to WMO) | ✅ Implemented | `weather_widgets.py` `ICON_MAP`; text descriptions preserved |
| Responsive / resizable | ✅ Implemented | `root.minsize()`; scrollable canvas; expandable frames |
| Background threading | ✅ Implemented | `threading.Thread` + `root.after(0, ...)` |
| Stale result protection | ✅ Implemented | `search_counter` ignores outdated callbacks |
| Attribution visible | ✅ Implemented | `"Weather data by Open-Meteo.com"` label |

**Not fully verified against PDF** because `OASIS INFOBYTE — Task List.pdf` was not found in workspace or web-accessible sources. The checklist above reflects only the user's pasted specification.

---

## Manual Testing (No Fake Screenshots)

To capture genuine screenshots:

1. `python app.py`
2. Search `London` → wait for results
3. Press **Windows + Shift + S**
4. Save to `Python-Task4-WeatherApp/screenshots/`
5. Toggle to °F and capture again
6. Search `Paris,FR` for international test

No fabricated screenshots are included.

---

## Testing with Real Network

If internet is available, try:
```python
from weather_service import WeatherService
s = WeatherService()
w = s.get_current_weather("Berlin", units="metric")
print(w['city'], w['temperature'], w.get('hourly',[])[:2])
```

If offline, tests pass entirely via mocks.

---

## Known Limitations

- Forecast limited by Open-Meteo free tier (7 days, 168 hourly points)
- Only English interface
- No forecast history persistence
- Icons are Unicode symbols (work on most fonts; may vary by OS)

---

## Source of Specification

This upgrade was guided by the user's pasted requirements (current + hourly + daily + cards + icons + responsive). The original `OASIS INFOBYTE — Task List.pdf` was **not found** in the workspace (`OIBSIP/` root or nearby directories) or via web fetch; therefore full PDF compliance is not claimed.

---

## API Attribution

Weather data provided by [Open-Meteo](https://open-meteo.com/).  
Attribution label visible in application.
