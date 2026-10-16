# BMI Calculator - Browser Version

**Web-based BMI Calculator with Local Storage History**

This is the **browser-based version** of the BMI Calculator. It runs entirely in your web browser using HTML, CSS, and JavaScript.

---

## 🌐 How to Use

### Open in Chrome (or Any Browser)

**Option 1: Double-click the file**
1. Navigate to `Python-Task2-BMICalculator\web-version\`
2. Double-click `index.html`
3. It will open in your default browser

**Option 2: Open from Chrome**
1. Open Google Chrome
2. Press `Ctrl + O` (or File → Open File)
3. Navigate to `Python-Task2-BMICalculator\web-version\index.html`
4. Click Open

**Option 3: Right-click method**
1. Right-click `index.html`
2. Choose "Open with"
3. Select "Google Chrome"

---

## ✨ Features

### Core Features
- ✅ Calculate BMI from weight (kg) and height (metres)
- ✅ WHO category classification with color coding
- ✅ Real-time input validation
- ✅ Responsive design (works on mobile and desktop)
- ✅ Dark mode support (automatic based on system preference)

### Advanced Features
- ✅ **Local storage history** - Saves your BMI records in browser
- ✅ **Username support** - Track records for multiple users
- ✅ **History view** - See all past calculations
- ✅ **Trend chart** - Interactive Chart.js visualization (requires 2+ records)
- ✅ **Automatic username suggestions** - Dropdown of previously used names

---

## 📊 How It Works

### Browser Storage
- Records are saved in **browser localStorage**
- Data persists across browser sessions
- Each browser has separate storage (not synced between devices)
- Private browsing mode may not save history

### Privacy
- All calculations happen locally in your browser
- No data is sent to any server
- No internet connection required (after first load for Chart.js)
- Clear your browser data to remove history

---

## 🎨 Design Features

### Responsive Layout
- Works on phones (400px+), tablets, and desktops
- Touch-friendly interface
- Automatically adjusts layout for screen size

### Dark Mode
- Automatically detects system theme preference
- Consistent colors in both light and dark modes
- Easy on the eyes in any lighting

### Accessibility
- Keyboard navigation support
- Clear error messages
- High contrast text
- Focus indicators on interactive elements

---

## 🔄 Differences from Python Version

| Feature | Python (tkinter) | Browser (HTML/JS) |
|---------|------------------|-------------------|
| **Storage** | SQLite database file | Browser localStorage |
| **Platform** | Windows/Mac/Linux desktop | Any device with browser |
| **History Sharing** | Shared on same computer | Per-browser, not shared |
| **Offline Use** | Fully offline | Needs Chart.js CDN on first load |
| **Multi-user** | True multi-user database | Browser-local tracking |
| **Installation** | Requires Python setup | No installation needed |

---

## 📝 Usage Instructions

### Calculate Your BMI

1. **Enter Name** (optional) - Type your name to save history
2. **Enter Weight** - In kilograms (e.g., 70)
3. **Enter Height** - In metres (e.g., 1.75)
4. **Click "Calculate BMI"** or press Enter
5. Your result appears with color-coded category

### View History

1. Enter calculations with a username
2. Click **"View History"**
3. See all your past records
4. Interactive trend chart appears (with 2+ records)

### Clear History

To clear all stored history:
1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Type: `localStorage.clear()`
4. Press Enter
5. Refresh the page

---

## 🛠 Technologies Used

- **HTML5** - Page structure
- **CSS3** - Styling with CSS custom properties
- **JavaScript (ES6+)** - Logic and interactivity
- **Chart.js 4.4.0** - Trend visualization (loaded from CDN)
- **localStorage API** - Browser-based storage

---

## 🎯 Technical Details

### Input Validation
- Weight: 0 < weight ≤ 500 kg
- Height: 0.5 ≤ height ≤ 3.0 metres
- Non-numeric inputs rejected
- Empty fields rejected

### BMI Categories
- **Underweight**: BMI < 18.5 (Blue)
- **Normal**: BMI 18.5–24.9 (Green)
- **Overweight**: BMI 25–29.9 (Orange)
- **Obese**: BMI ≥ 30 (Red)

### Storage Limits
- Stores last 50 BMI records
- Automatically removes oldest records when limit reached
- Each record stores: name, weight, height, BMI, category, timestamp

---

## ⚠️ Limitations

1. **Browser-specific storage** - Records don't sync between browsers/devices
2. **No server backup** - Clearing browser data loses history
3. **Single-user per browser** - No true multi-user authentication
4. **Internet needed once** - Chart.js loads from CDN on first use
5. **Private browsing** - May not save history depending on browser

---

## 🔗 Comparison with Python Version

### When to Use Browser Version
- ✅ Quick calculations without setup
- ✅ Want to access from any device
- ✅ Don't need permanent storage
- ✅ Prefer modern web interface
- ✅ Want to share easily (just send the HTML file)

### When to Use Python Version
- ✅ Need permanent SQLite database
- ✅ Want true multi-user support
- ✅ Need complete offline functionality
- ✅ Building for internship submission
- ✅ Prefer desktop application

---

## 📄 License

This web version is developed as part of the Oasis Infobyte Python Programming internship to demonstrate full-stack development skills.

---

## 🆘 Troubleshooting

### Chart not showing
- Check internet connection (Chart.js loads from CDN)
- Make sure you have at least 2 BMI records
- Try refreshing the page

### History not saving
- Check if you're in private/incognito mode
- Verify browser allows localStorage
- Check browser storage quota

### Page not opening
- Make sure file extension is `.html`
- Try opening in different browser
- Check file wasn't corrupted during copy

---

**Note**: This browser version complements the main Python tkinter application. Both versions demonstrate the same BMI calculation logic with different presentation layers.

**Last Updated**: October 13, 2026
