"""
Weather App - Tkinter GUI Application (Advanced Dashboard)

Premium weather dashboard with current conditions, hourly forecast,
daily forecast, metric cards, weather icons, and responsive design.
Open-Meteo API — no API key required.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import threading
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather_service import (
    WeatherService, WeatherServiceError, CityNotFoundError, NetworkError
)
from weather_widgets import get_icon_text, get_icon_desc

# Dark purple premium palette (approximation — reference image not available)
BG = "#1a0b2e"
CARD_BG = "#2d1b4e"
ACCENT = "#c084fc"  # lavender
TEXT = "#f8fafc"
SUB = "#9ca3af"
CARD_BORDER = "#3d2065"


def _now_time():
    return datetime.now().strftime("%H:%M")


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Dashboard — Open-Meteo")
        self.root.geometry("900x780")
        self.root.minsize(780, 640)
        self.root.configure(bg=BG)
        self.current_units = "metric"
        self.current_weather = None
        self.service = WeatherService()
        self.search_counter = 0  # prevent stale results
        self.setup_styles()
        self.create_widgets()
        self.root.bind('<Return>', lambda e: self.search_weather())
        self.root.bind('<Control-r>', lambda e: self.search_weather())
        self.city_entry.focus()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=BG)
        style.configure('Search.TButton', font=('Segoe UI', 11, 'bold'),
                        background=ACCENT, foreground='#0f172a', padding=10)
        style.configure('Unit.TButton', font=('Segoe UI', 9, 'bold'),
                        padding=6)
        style.map('Unit.TButton', background=[('active', '#1e293b'), ('!active', '#334155')])

    def create_widgets(self):
        # Main scrollable canvas
        self.canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self.scroll = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=BG)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all"), width=e.width))

        # Main layout: left sidebar + main content area
        container = tk.Frame(self.inner, bg=BG)
        container.pack(fill="both", expand=True, padx=20, pady=10)
        container.columnconfigure(1, weight=1)

        # --- Left sidebar ---
        sidebar = tk.Frame(container, bg="#140828", width=180)
        sidebar.pack(side="left", fill="y", padx=(0, 16))
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="WEATHER", font=("Segoe UI", 18, "bold"),
                 bg="#140828", fg=ACCENT).pack(pady=(24, 4))
        tk.Label(sidebar, text="Dashboard", font=("Segoe UI", 11),
                 bg="#140828", fg=SUB).pack(pady=(0, 12))
        tk.Label(sidebar, text="Open-Meteo API", font=("Segoe UI", 9),
                 bg="#140828", fg="#6b5b7f").pack(pady=(0, 24))

        tk.Label(sidebar, text="Navigation", font=("Segoe UI", 9, "bold"),
                 bg="#140828", fg=SUB).pack(anchor="w", padx=14)
        tk.Label(sidebar, text="• Current Conditions", font=("Segoe UI", 9),
                 bg="#140828", fg=TEXT).pack(anchor="w", padx=20, pady=2)
        tk.Label(sidebar, text="• 24-Hour Forecast", font=("Segoe UI", 9),
                 bg="#140828", fg=TEXT).pack(anchor="w", padx=20, pady=2)
        tk.Label(sidebar, text="• 7-Day Outlook", font=("Segoe UI", 9),
                 bg="#140828", fg=TEXT).pack(anchor="w", padx=20, pady=2)

        # Divider line
        tk.Frame(sidebar, bg="#3d2065", height=1).pack(fill="x", padx=14, pady=16)

        # Units in sidebar
        tk.Label(sidebar, text="Units", font=("Segoe UI", 9, "bold"),
                 bg="#140828", fg=SUB).pack(anchor="w", padx=14)
        btns = tk.Frame(sidebar, bg="#140828")
        btns.pack(anchor="w", padx=14, pady=6)
        self.c_btn = tk.Button(btns, text="°C", command=lambda: self.set_units("metric"),
                              bg=ACCENT, fg="#0f0f0f", font=("Segoe UI", 10, "bold"),
                              relief="flat", padx=10, pady=4, cursor="hand2")
        self.c_btn.pack(side="left", padx=(0, 6))
        self.f_btn = tk.Button(btns, text="°F", command=lambda: self.set_units("imperial"),
                              bg="#2d1b4e", fg=SUB, font=("Segoe UI", 10, "bold"),
                              relief="flat", padx=10, pady=4, cursor="hand2")
        self.f_btn.pack(side="left")

        # Attribution at bottom of sidebar
        tk.Label(sidebar, text="Data: Open-Meteo.com",
                 font=("Segoe UI", 8), bg="#140828", fg="#6b5b7f").pack(side="bottom", pady=12)

        # --- Main content area ---
        main = tk.Frame(container, bg=BG)
        main.pack(side="left", fill="both", expand=True)
        main.columnconfigure(0, weight=1)

        # Header row inside main
        header = tk.Frame(main, bg=BG)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="Weather Dashboard", font=("Segoe UI", 24, "bold"),
                 bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(header, text="Real-time forecasts • Open-Meteo • No API key required",
                 font=("Segoe UI", 9), bg=BG, fg=SUB).pack(anchor="w", pady=(0, 2))

        # Search bar inside main
        search_frame = tk.Frame(main, bg=CARD_BG, padx=16, pady=14)
        search_frame.pack(fill="x", pady=(0, 14))
        search_frame.columnconfigure(2, weight=1)
        tk.Label(search_frame, text="Search city:", font=("Segoe UI", 11, "bold"),
                 bg=CARD_BG, fg=TEXT).grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.city_var = tk.StringVar()
        self.city_entry = tk.Entry(search_frame, textvariable=self.city_var,
                                   font=("Segoe UI", 13), bg="#1a0b2e", fg=TEXT,
                                   insertbackground=TEXT, relief="flat", bd=0,
                                   highlightthickness=2, highlightbackground=ACCENT)
        self.city_entry.grid(row=0, column=2, sticky="ew", padx=6)
        self.search_btn = tk.Button(search_frame, text="Search  ⏎", command=self.search_weather,
                                   bg=ACCENT, fg="#0f0f0f", font=("Segoe UI", 11, "bold"),
                                   activebackground="#a855f7", relief="flat", padx=16, pady=7,
                                   cursor="hand2")
        self.search_btn.grid(row=0, column=4, sticky="e", padx=(4, 0))

        self.search_btn.config(state="normal", text="Search  ⏎")

        # --- Current weather card (compact) ---
        current_frame = tk.Frame(main, bg=CARD_BG, relief="flat", bd=0,
                                  highlightbackground=CARD_BORDER, highlightthickness=1)
        current_frame.pack(fill="x", pady=6)
        current_inner = tk.Frame(current_frame, bg=CARD_BG)
        current_inner.pack(padx=16, pady=14)
        # Top row: location left, icon right
        top = tk.Frame(current_inner, bg=CARD_BG)
        top.pack(fill="x")
        self.city_name_lbl = tk.Label(top, text="Weather Dashboard", font=("Segoe UI", 16, "bold"),
                                      bg=CARD_BG, fg=TEXT)
        self.city_name_lbl.pack(side="left")
        self.icon_lbl = tk.Label(top, text="⏳", font=("Segoe UI", 28), bg=CARD_BG, fg=ACCENT)
        self.icon_lbl.pack(side="right")
        # Temp + desc compact
        mid = tk.Frame(current_inner, bg=CARD_BG)
        mid.pack(fill="x", pady=(6, 4))
        self.temp_big = tk.Label(mid, text="--°", font=("Segoe UI", 42, "bold"),
                                  bg=CARD_BG, fg=TEXT)
        self.temp_big.pack(side="left")
        self.desc_lbl = tk.Label(mid, text="Enter a city and search", font=("Segoe UI", 11),
                                 bg=CARD_BG, fg=SUB)
        self.desc_lbl.pack(side="left", padx=10)
        # Metrics row (4 cards, equal size)
        metrics = tk.Frame(current_inner, bg=CARD_BG)
        metrics.pack(fill="x", pady=(8, 0))
        labels = [("Feels like", "feels_like"), ("Humidity", "humidity"),
                  ("Wind", "wind_speed"), ("Pressure", "pressure")]
        for i, (label, key) in enumerate(labels):
            f = tk.Frame(metrics, bg="#140828", relief="flat", bd=0)
            f.grid(row=0, column=i, sticky="ew", padx=4)
            f.columnconfigure(0, weight=1)
            tk.Label(f, text=label, font=("Segoe UI", 8, "bold"), bg="#140828", fg=SUB).pack(pady=(6, 1))
            self.metric_vars = getattr(self, 'metric_vars', {})
            self.metric_vars[label] = tk.Label(f, text="--", font=("Segoe UI", 11, "bold"),
                                                bg="#140828", fg=TEXT)
            self.metric_vars[label].pack(pady=(0, 6))
            metrics.columnconfigure(i, weight=1)
        self.metric_vars = self.metric_vars

        # Hourly forecast title
        hourly_title = tk.Label(main, text="Next 24 Hours", font=("Segoe UI", 16, "bold"),
                                bg=BG, fg=TEXT)
        hourly_title.pack(anchor="w", pady=(14, 4))
        # Hourly scroll strip
        hourly_outer = tk.Frame(main, bg=BG)
        hourly_outer.pack(fill="x")
        self.hourly_frame = tk.Frame(hourly_outer, bg=BG)
        self.hourly_frame.pack(fill="x")
        self.hourly_canvas = tk.Canvas(self.hourly_frame, bg=BG, highlightthickness=0, height=150)
        self.hourly_scroll = ttk.Scrollbar(hourly_outer, orient="horizontal",
                                           command=self.hourly_canvas.xview)
        self.hourly_canvas.configure(xscrollcommand=self.hourly_scroll.set)
        self.hourly_scroll.pack(side="bottom", fill="x")
        self.hourly_canvas.pack(side="top", fill="both", expand=True)
        self.hourly_inner = tk.Frame(self.hourly_canvas, bg=BG)
        self.hourly_window = self.hourly_canvas.create_window((0, 0), window=self.hourly_inner, anchor="nw")
        self.hourly_inner.bind("<Configure>", lambda e: self.hourly_canvas.configure(
            scrollregion=self.hourly_canvas.bbox("all")))

        # Daily forecast title
        daily_title = tk.Label(main, text="7-Day Forecast", font=("Segoe UI", 16, "bold"),
                               bg=BG, fg=TEXT)
        daily_title.pack(anchor="w", pady=(16, 4))
        # Daily cards scroll frame (horizontal wrap, scroll if needed)
        daily_outer = tk.Frame(main, bg=BG)
        daily_outer.pack(fill="x", pady=(0, 8))
        self.daily_frame = tk.Frame(daily_outer, bg=BG)
        self.daily_frame.pack(fill="x")

        # Status
        self.status_lbl = tk.Label(main, text="Ready", font=("Segoe UI", 9), bg=BG, fg=SUB)
        self.status_lbl.pack(anchor="w", pady=(8, 2))
        # Attribution inside main (not sidebar)
        attr = tk.Label(main, text="Weather data by Open-Meteo.com",
                        font=("Segoe UI", 8), bg=BG, fg="#6b5b7f")
        attr.pack(anchor="w", pady=(0, 6))

    # --- Actions ---

    def set_units(self, units):
        if units == self.current_units:
            return
        self.current_units = units
        self.c_btn.config(bg=ACCENT if units == "metric" else "#2d1b4e",
                          fg="#0f0f0f" if units == "metric" else SUB)
        self.f_btn.config(bg=ACCENT if units == "imperial" else "#2d1b4e",
                          fg="#0f0f0f" if units == "imperial" else SUB)
        if self.current_weather:
            self._update_weather_display(self.current_weather)

    def search_weather(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showwarning("Invalid Input", "Please enter a city name.")
            self.city_entry.focus(); return
        # Show temporary loading state (not permanent symbol)
        self.icon_lbl.config(text="⏳")
        self.desc_lbl.config(text="Fetching weather data...")
        self.temp_big.config(text="--°")
        self.city_name_lbl.config(text=city)
        self.search_btn.config(state="disabled", text="Searching...")
        self.status_lbl.config(text="Fetching weather data...", fg=ACCENT)
        self.search_counter += 1
        thread = threading.Thread(target=self._fetch_background,
                                  args=(city, self.current_units, self.search_counter),
                                  daemon=True)
        thread.start()

    def _fetch_background(self, city, units, counter):
        try:
            weather = self.service.get_current_weather(city, units=units)
            self.root.after(0, lambda w=weather, c=counter: self._on_result(w, c))
        except CityNotFoundError as e:
            self.root.after(0, lambda c=counter: self._show_error("City Not Found", str(e), c))
        except NetworkError as e:
            self.root.after(0, lambda c=counter: self._show_error("Network Error", str(e), c))
        except WeatherServiceError as e:
            self.root.after(0, lambda c=counter: self._show_error("Service Error", str(e), c))
        except Exception as e:
            self.root.after(0, lambda c=counter: self._show_error("Unexpected Error",
                          f"{e}", c))
        finally:
            self.root.after(0, lambda: self.search_btn.config(state="normal", text="Search  ⏎"))

    def _on_result(self, weather, counter):
        if counter != self.search_counter:
            return  # stale; ignore
        self.current_weather = weather
        self._update_weather_display(weather)
        self.status_lbl.config(text=f"Last updated {_now_time()}", fg="#4ade80")

    def _show_error(self, title, msg, counter):
        if counter != self.search_counter:
            return
        messagebox.showerror(title, msg)
        self.status_lbl.config(text="Error — please try again.", fg="#f87171")

    def _update_weather_display(self, w):
        # City + icon + big temp
        self.city_name_lbl.config(text=f"{w['city']}, {w['country']}")
        self.icon_lbl.config(text=get_icon_text(w.get('weather_code', 0)))
        sym = "°C" if w['units'] == "metric" else "°F"
        self.temp_big.config(text=f"{w['temperature']}{sym}")
        self.desc_lbl.config(text=w['description'])
        # Metrics — display honestly; do not invent missing pressure
        for label, key in [("Feels like", "feels_like"), ("Humidity", "humidity"),
                           ("Wind", "wind_speed"), ("Pressure", "pressure")]:
            raw = w.get(key)
            # Treat None / missing as unavailable; 0 for pressure is also unavailable from open-meteo
            if raw is None:
                val = "--"
            elif isinstance(raw, (int, float)):
                if key == "pressure" and raw == 0:
                    val = "N/A"
                else:
                    val = raw
                    if label == "Feels like":
                        val = f"{val}{sym}"
                    elif label == "Humidity":
                        val = f"{val}%"
                    elif label == "Wind":
                        unit = "m/s" if w['units'] == "metric" else "mph"
                        val = f"{val} {unit}"
                    elif label == "Pressure":
                        val = f"{val} hPa"
            else:
                val = str(raw)
            self.metric_vars[label].config(text=str(val))
        # Hourly strip
        self._build_hourly(w.get('hourly', []), w['units'])
        # Daily cards
        self._build_daily(w.get('daily', []), w['units'])

    def _build_hourly(self, hourly, units):
        # Clear old
        for child in self.hourly_inner.winfo_children():
            child.destroy()
        if not hourly:
            tk.Label(self.hourly_inner, text="Forecast unavailable", font=("Segoe UI", 10),
                     bg=BG, fg=SUB).pack(padx=10)
            return
        sym = "°C" if units == "metric" else "°F"
        for i, item in enumerate(hourly[:24]):
            card = tk.Frame(self.hourly_inner, bg=CARD_BG, relief="ridge", bd=1,
                            highlightbackground="#334155")
            card.pack(side="left", padx=4)
            t_str = item['time']
            # Show hour only
            try:
                t_display = t_str.split('T')[-1][:5] if 'T' in t_str else t_str[-8:-3]
            except Exception:
                t_display = t_str[-8:-3] if len(t_str) > 5 else t_str
            tk.Label(card, text=t_display, font=("Segoe UI", 9, "bold"),
                     bg=CARD_BG, fg=TEXT).pack(pady=(6, 0))
            tk.Label(card, text=get_icon_text(item.get('weather_code', 0)),
                     font=("Segoe UI", 20), bg=CARD_BG, fg=ACCENT).pack()
            temp = item.get('temperature')
            if temp is not None:
                tk.Label(card, text=f"{temp}{sym}", font=("Segoe UI", 11, "bold"),
                         bg=CARD_BG, fg=TEXT).pack()
            else:
                tk.Label(card, text="--", font=("Segoe UI", 11), bg=CARD_BG, fg=SUB).pack()
            prec = item.get('precipitation_probability', 0)
            if prec:
                tk.Label(card, text=f"☔ {prec}%", font=("Segoe UI", 8),
                         bg=CARD_BG, fg="#f87171").pack(pady=(2, 6))
            else:
                tk.Label(card, text="", bg=CARD_BG).pack(pady=(2, 6))
        self.hourly_inner.update_idletasks()
        self.hourly_canvas.configure(scrollregion=self.hourly_canvas.bbox("all"))

    def _build_daily(self, daily, units):
        for c in self.daily_frame.winfo_children():
            c.destroy()
        if not daily:
            tk.Label(self.daily_frame, text="Daily forecast unavailable",
                     font=("Segoe UI", 10), bg=BG, fg=SUB).pack(anchor="w")
            return
        sym = "°C" if units == "metric" else "°F"
        for item in daily[:7]:
            card = tk.Frame(self.daily_frame, bg=CARD_BG, relief="ridge", bd=1,
                            highlightbackground="#334155")
            card.pack(side="left", fill="y", padx=6, pady=4, expand=True)
            # Day label
            d_str = item.get('date', '')
            try:
                from datetime import datetime as dt
                day_name = dt.fromisoformat(d_str.replace('Z', '+00:00')).strftime("%a")
            except Exception:
                day_name = d_str[:3] if len(d_str) >= 3 else d_str
            tk.Label(card, text=day_name, font=("Segoe UI", 12, "bold"),
                     bg=CARD_BG, fg=TEXT).pack(pady=(10, 2))
            tk.Label(card, text=get_icon_text(item.get('weather_code', 0)),
                     font=("Segoe UI", 28), bg=CARD_BG, fg=ACCENT).pack()
            tk.Label(card, text=get_icon_desc(item.get('weather_code', 0)),
                     font=("Segoe UI", 9), bg=CARD_BG, fg=SUB).pack(pady=(0, 6))
            max_t = item.get('max_temp')
            min_t = item.get('min_temp')
            if max_t is not None and min_t is not None:
                tk.Label(card, text=f"{max_t}{sym} / {min_t}{sym}",
                         font=("Segoe UI", 11, "bold"), bg=CARD_BG, fg=TEXT).pack()
            else:
                tk.Label(card, text="-- / --", font=("Segoe UI", 11), bg=CARD_BG, fg=SUB).pack()


# Entry
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
