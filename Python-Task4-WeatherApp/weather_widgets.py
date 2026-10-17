"""Weather dashboard widgets — cards, hourly strip, daily cards, icons."""
import tkinter as tk
from tkinter import ttk

ICON_MAP = {
    0: ("☀", "Clear sky"),
    1: ("🌤", "Mainly clear"),
    2: ("⛅", "Partly cloudy"),
    3: ("☁", "Overcast"),
    45: ("🌫", "Foggy"),
    48: ("🌫", "Depositing rime fog"),
    51: ("🌦", "Light drizzle"),
    53: ("🌧", "Moderate drizzle"),
    55: ("🌧", "Dense drizzle"),
    56: ("🌨", "Light freezing drizzle"),
    57: ("🌨", "Dense freezing drizzle"),
    61: ("🌧", "Slight rain"),
    63: ("🌧", "Moderate rain"),
    65: ("🌧", "Heavy rain"),
    66: ("🌨", "Light freezing rain"),
    67: ("🌨", "Heavy freezing rain"),
    71: ("❄", "Slight snow"),
    73: ("❄", "Moderate snow"),
    75: ("❄", "Heavy snow"),
    77: ("❄", "Snow grains"),
    80: ("🌦", "Slight rain showers"),
    81: ("🌧", "Moderate rain showers"),
    82: ("🌧", "Violent rain showers"),
    85: ("🌨", "Slight snow showers"),
    86: ("🌨", "Heavy snow showers"),
    95: ("⛈", "Thunderstorm"),
    96: ("⛈", "Thunderstorm with slight hail"),
    99: ("⛈", "Thunderstorm with heavy hail"),
}


def get_icon_text(code):
    return ICON_MAP.get(code, ("?", "Unknown"))[0]


def get_icon_desc(code):
    return ICON_MAP.get(code, ("?", "Unknown"))[1]


class MetricCard(ttk.Frame):
    def __init__(self, parent, label, value, sub=""):
        super().__init__(parent, relief="ridge", padding=8)
        ttk.Label(self, text=label, font=("Segoe UI", 9), foreground="#555").pack(anchor="w")
        ttk.Label(self, text=str(value), font=("Segoe UI", 14, "bold"), foreground="#222").pack(anchor="w")
        if sub:
            ttk.Label(self, text=sub, font=("Segoe UI", 8), foreground="#777").pack(anchor="w")
