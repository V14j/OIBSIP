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

        # Centered container with max width for responsive layout
        self.container = tk.Frame(self.inner, bg=BG)
        self.container.pack(expand=True, fill='both', padx=24, pady=16)
        self.container.columnconfigure(0, weight=1)

        # Track container width for centering
        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # --- Header ---
        header = tk.Frame(self.container, bg=BG)
        header.grid(row=0, column=0, sticky='ew', pady=(0, 16))
        header.columnconfigure(0, weight=1)

        # Accent line
        accent_line = tk.Frame(header, bg=ACCENT, height=3)
        accent_line.grid(row=0, column=0, sticky='ew', pady=(0, 10))

        tk.Label(header, text="Weather Dashboard", font=("Segoe UI", 28, "bold"),
                 bg=BG, fg=TEXT).grid(row=1, column=0, sticky='w')
        tk.Label(header, text="Real-time forecasts • Open-Meteo • No API key required",
                 font=("Segoe UI", 10), bg=BG, fg=SUB).grid(row=2, column=0, sticky='w', pady=(4, 0))

        # Search bar card
        search_card = tk.Frame(self.container, bg=CARD_BG,
                                highlightbackground=CARD_BORDER, highlightthickness=1)
        search_card.grid(row=1, column=0, sticky='ew', pady=(0, 16))
        search_card.columnconfigure(1, weight=1)

        search_inner = tk.Frame(search_card, bg=CARD_BG)
        search_inner.pack(fill='x', padx=20, pady=16)
        search_inner.columnconfigure(1, weight=1)

        tk.Label(search_inner, text="Search City", font=("Segoe UI", 11, "bold"),
                 bg=CARD_BG, fg=TEXT).grid(row=0, column=0, sticky='w', padx=(0, 16))

        self.city_var = tk.StringVar()
        self.city_entry = tk.Entry(search_inner, textvariable=self.city_var,
                                   font=("Segoe UI", 13), bg="#1a0b2e", fg=TEXT,
                                   insertbackground=TEXT, relief="flat", bd=0,
                                   highlightthickness=2, highlightbackground=ACCENT)
        self.city_entry.grid(row=0, column=1, sticky="ew", padx=8)

        # Unit buttons in search row
        unit_frame = tk.Frame(search_inner, bg=CARD_BG)
        unit_frame.grid(row=0, column=2, sticky='e', padx=(8, 0))

        self.c_btn = tk.Button(unit_frame, text="°C", command=lambda: self.set_units("metric"),
                              bg=ACCENT, fg="#0f0f0f", font=("Segoe UI", 10, "bold"),
                              relief="flat", padx=14, pady=7, cursor="hand2",
                              bd=0, activebackground="#a855f7", activeforeground="#0f0f0f")
        self.c_btn.pack(side="left", padx=(0, 6))
        self.f_btn = tk.Button(unit_frame, text="°F", command=lambda: self.set_units("imperial"),
                              bg="#2d1b4e", fg=SUB, font=("Segoe UI", 10, "bold"),
                              relief="flat", padx=14, pady=7, cursor="hand2",
                              bd=1, highlightbackground="#3d2065", highlightthickness=1,
                              activebackground="#3d2065", activeforeground=TEXT)
        self.f_btn.pack(side="left")

        self.search_btn = tk.Button(search_inner, text="Search  ⏎", command=self.search_weather,
                                   bg=ACCENT, fg="#0f0f0f", font=("Segoe UI", 11, "bold"),
                                   activebackground="#a855f7", relief="flat", padx=20, pady=7,
                                   cursor="hand2")
        self.search_btn.grid(row=0, column=3, sticky="e", padx=(8, 0))

        # --- Current weather card (primary focus) ---
        current_frame = tk.Frame(self.container, bg=CARD_BG, relief="flat", bd=0,
                                  highlightbackground=CARD_BORDER, highlightthickness=1)
        current_frame.grid(row=2, column=0, sticky='ew', pady=(0, 16))

        current_inner = tk.Frame(current_frame, bg=CARD_BG)
        current_inner.pack(fill='x', padx=24, pady=20)

        # Top row: location left, icon right
        top = tk.Frame(current_inner, bg=CARD_BG)
        top.pack(fill="x")
        self.city_name_lbl = tk.Label(top, text="Weather Dashboard", font=("Segoe UI", 20, "bold"),
                                      bg=CARD_BG, fg=TEXT)
        self.city_name_lbl.pack(side="left")
        self.icon_lbl = tk.Label(top, text="☀️", font=("Segoe UI", 40), bg=CARD_BG, fg=ACCENT)
        self.icon_lbl.pack(side="right")

        # Temp + desc
        mid = tk.Frame(current_inner, bg=CARD_BG)
        mid.pack(fill="x", pady=(10, 8))
        self.temp_big = tk.Label(mid, text="--°", font=("Segoe UI", 56, "bold"),
                                  bg=CARD_BG, fg=TEXT)
        self.temp_big.pack(side="left")
        self.desc_lbl = tk.Label(mid, text="Enter a city and search", font=("Segoe UI", 13),
                                 bg=CARD_BG, fg=SUB)
        self.desc_lbl.pack(side="left", padx=16, pady=(14, 0))

        # Metrics row (4 cards, equal width)
        metrics = tk.Frame(current_inner, bg=CARD_BG)
        metrics.pack(fill="x", pady=(12, 0))
        labels = [("Feels Like", "feels_like"), ("Humidity", "humidity"),
                  ("Wind", "wind_speed"), ("Pressure", "pressure")]
        for i in range(4):
            metrics.columnconfigure(i, weight=1, uniform="metrics")
        self.metric_vars = {}
        for i, (label, key) in enumerate(labels):
            f = tk.Frame(metrics, bg="#1a0b2e", relief="flat", bd=0)
            f.grid(row=0, column=i, sticky="nsew", padx=6)
            f.columnconfigure(0, weight=1)
            f.rowconfigure(0, weight=1)
            f.rowconfigure(1, weight=1)
            tk.Label(f, text=label, font=("Segoe UI", 9, "bold"), bg="#1a0b2e", fg=SUB).pack(pady=(10, 2))
            self.metric_vars[label] = tk.Label(f, text="--", font=("Segoe UI", 13, "bold"),
                                                bg="#1a0b2e", fg=TEXT)
            self.metric_vars[label].pack(pady=(0, 10))

        # Hourly forecast section
        hourly_section = tk.Frame(self.container, bg=BG)
        hourly_section.grid(row=3, column=0, sticky='ew', pady=(0, 16))
        hourly_section.columnconfigure(0, weight=1)

        hourly_header = tk.Frame(hourly_section, bg=BG)
        hourly_header.pack(fill='x', pady=(0, 8))
        tk.Label(hourly_header, text="Next 24 Hours", font=("Segoe UI", 18, "bold"),
                bg=BG, fg=TEXT).pack(side='left')

        # Hourly scroll strip with horizontal scrollbar
        hourly_outer = tk.Frame(hourly_section, bg=BG)
        hourly_outer.pack(fill="x")
        self.hourly_canvas = tk.Canvas(hourly_outer, bg=BG, highlightthickness=0, height=160)
        self.hourly_scroll = ttk.Scrollbar(hourly_outer, orient="horizontal",
                                           command=self.hourly_canvas.xview)
        self.hourly_canvas.configure(xscrollcommand=self.hourly_scroll.set)
        self.hourly_scroll.pack(side="bottom", fill="x")
        self.hourly_canvas.pack(side="top", fill="both", expand=True)
        self.hourly_inner = tk.Frame(self.hourly_canvas, bg=BG)
        self.hourly_window = self.hourly_canvas.create_window((0, 0), window=self.hourly_inner, anchor="nw")
        self.hourly_inner.bind("<Configure>", lambda e: self.hourly_canvas.configure(
            scrollregion=self.hourly_canvas.bbox("all")))
        # Bind mouse wheel to horizontal scroll
        self.hourly_canvas.bind("<Enter>", lambda e: self.hourly_canvas.bind_all("<MouseWheel>", self._on_hourly_mousewheel))
        self.hourly_canvas.bind("<Leave>", lambda e: self.hourly_canvas.unbind_all("<MouseWheel>"))

        # Daily forecast section
        daily_section = tk.Frame(self.container, bg=BG)
        daily_section.grid(row=4, column=0, sticky='ew', pady=(0, 16))
        daily_section.columnconfigure(0, weight=1)

        daily_header = tk.Frame(daily_section, bg=BG)
        daily_header.pack(fill='x', pady=(0, 8))
        tk.Label(daily_header, text="7-Day Forecast", font=("Segoe UI", 18, "bold"),
                bg=BG, fg=TEXT).pack(side='left')

        daily_outer = tk.Frame(daily_section, bg=BG)
        daily_outer.pack(fill="x")
        self.daily_canvas = tk.Canvas(daily_outer, bg=BG, highlightthickness=0, height=200)
        self.daily_scroll = ttk.Scrollbar(daily_outer, orient="horizontal",
                                          command=self.daily_canvas.xview)
        self.daily_canvas.configure(xscrollcommand=self.daily_scroll.set)
        self.daily_scroll.pack(side="bottom", fill="x")
        self.daily_canvas.pack(side="top", fill="both", expand=True)
        self.daily_inner = tk.Frame(self.daily_canvas, bg=BG)
        self.daily_window = self.daily_canvas.create_window((0, 0), window=self.daily_inner, anchor="nw")
        self.daily_inner.bind("<Configure>", lambda e: self.daily_canvas.configure(
            scrollregion=self.daily_canvas.bbox("all")))
        self.daily_canvas.bind("<Enter>", lambda e: self.daily_canvas.bind_all("<MouseWheel>", self._on_daily_mousewheel))
        self.daily_canvas.bind("<Leave>", lambda e: self.daily_canvas.unbind_all("<MouseWheel>"))

        # Status and attribution
        bottom = tk.Frame(self.container, bg=BG)
        bottom.grid(row=5, column=0, sticky='ew', pady=(8, 0))
        self.status_lbl = tk.Label(bottom, text="Ready", font=("Segoe UI", 9), bg=BG, fg=SUB)
        self.status_lbl.pack(anchor="w")
        attr = tk.Label(bottom, text="Weather data by Open-Meteo.com",
                        font=("Segoe UI", 8), bg=BG, fg="#6b5b7f")
        attr.pack(anchor="w", pady=(4, 0))

    def _on_inner_configure(self, event):
        """Update scroll region when inner content changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Center container horizontally when canvas resizes."""
        canvas_width = event.width
        max_content_width = 1100
        content_width = min(canvas_width - 48, max_content_width)  # account for padding
        self.canvas.itemconfig(self.canvas_window, width=content_width)

    # --- Actions ---

    def _on_hourly_mousewheel(self, event):
        """Handle mouse wheel scrolling on hourly strip."""
        self.hourly_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def set_units(self, units):
        if units == self.current_units:
            return
        self.current_units = units
        if units == "metric":
            self.c_btn.config(bg=ACCENT, fg="#0f0f0f", bd=0, highlightthickness=0)
            self.f_btn.config(bg="#2d1b4e", fg=SUB, bd=1, highlightbackground="#3d2065", highlightthickness=1)
        else:
            self.c_btn.config(bg="#2d1b4e", fg=SUB, bd=1, highlightbackground="#3d2065", highlightthickness=1)
            self.f_btn.config(bg=ACCENT, fg="#0f0f0f", bd=0, highlightthickness=0)
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

    def _on_daily_mousewheel(self, event):
        """Handle mouse wheel scrolling on daily cards."""
        self.daily_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

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
            card = tk.Frame(self.hourly_inner, bg=CARD_BG, relief="flat", bd=0,
                            highlightbackground=CARD_BORDER, highlightthickness=1)
            card.pack(side="left", padx=6, pady=4)
            card.pack_propagate(False)
            card.configure(width=80)
            t_str = item['time']
            # Show hour only
            try:
                t_display = t_str.split('T')[-1][:5] if 'T' in t_str else t_str[-8:-3]
            except Exception:
                t_display = t_str[-8:-3] if len(t_str) > 5 else t_str
            tk.Label(card, text=t_display, font=("Segoe UI", 10, "bold"),
                     bg=CARD_BG, fg=TEXT).pack(pady=(10, 2))
            tk.Label(card, text=get_icon_text(item.get('weather_code', 0)),
                     font=("Segoe UI", 24), bg=CARD_BG, fg=ACCENT).pack(pady=4)
            temp = item.get('temperature')
            if temp is not None:
                tk.Label(card, text=f"{temp}{sym}", font=("Segoe UI", 12, "bold"),
                         bg=CARD_BG, fg=TEXT).pack()
            else:
                tk.Label(card, text="--", font=("Segoe UI", 12), bg=CARD_BG, fg=SUB).pack()
            prec = item.get('precipitation_probability', 0)
            if prec:
                tk.Label(card, text=f"☔ {prec}%", font=("Segoe UI", 8),
                         bg=CARD_BG, fg="#f87171").pack(pady=(2, 8))
            else:
                tk.Label(card, text="", bg=CARD_BG).pack(pady=(2, 8))
        self.hourly_inner.update_idletasks()
        self.hourly_canvas.configure(scrollregion=self.hourly_canvas.bbox("all"))

    def _build_daily(self, daily, units):
        for c in self.daily_inner.winfo_children():
            c.destroy()
        if not daily:
            tk.Label(self.daily_inner, text="Daily forecast unavailable",
                     font=("Segoe UI", 10), bg=BG, fg=SUB).pack(anchor="w", padx=10)
            return
        sym = "°C" if units == "metric" else "°F"
        for item in daily[:7]:
            card = tk.Frame(self.daily_inner, bg=CARD_BG, relief="flat", bd=0,
                            highlightbackground=CARD_BORDER, highlightthickness=1)
            card.pack(side="left", fill="y", padx=8, pady=4)
            card.pack_propagate(False)
            card.configure(width=120)
            # Day label
            d_str = item.get('date', '')
            try:
                from datetime import datetime as dt
                day_name = dt.fromisoformat(d_str.replace('Z', '+00:00')).strftime("%a %b %d")
            except Exception:
                day_name = d_str[:10] if len(d_str) >= 10 else d_str
            tk.Label(card, text=day_name, font=("Segoe UI", 11, "bold"),
                     bg=CARD_BG, fg=TEXT).pack(pady=(12, 2))
            tk.Label(card, text=get_icon_text(item.get('weather_code', 0)),
                     font=("Segoe UI", 32), bg=CARD_BG, fg=ACCENT).pack(pady=6)
            tk.Label(card, text=get_icon_desc(item.get('weather_code', 0)),
                     font=("Segoe UI", 9), bg=CARD_BG, fg=SUB).pack(pady=(0, 6))
            max_t = item.get('max_temp')
            min_t = item.get('min_temp')
            if max_t is not None and min_t is not None:
                tk.Label(card, text=f"H {max_t}{sym}  L {min_t}{sym}",
                         font=("Segoe UI", 11, "bold"), bg=CARD_BG, fg=TEXT).pack(pady=(0, 10))
            else:
                tk.Label(card, text="-- / --", font=("Segoe UI", 11), bg=CARD_BG, fg=SUB).pack(pady=(0, 10))


# Entry
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
