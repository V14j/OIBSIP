"""
Voice Assistant GUI Application — Premium Edition (OIBSIP Task 1)

Tkinter-based desktop interface for the voice assistant.
Handles microphone input, speech recognition, text-to-speech,
and conversation display in a responsive, thread-safe manner.

Thread-safety model: background threads (microphone listener, TTS
worker) NEVER touch Tkinter widgets directly. They push messages onto
``self.gui_queue``; the main thread polls that queue with
``root.after()`` and performs every GUI update itself.
"""

import math
import os
import queue
import random
import sys
import threading
import time
from datetime import datetime
from typing import Optional

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from assistant_core import VoiceAssistantCore, AssistantResponse

# Try to import speech recognition and TTS
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None  # type: ignore

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    pyttsx3 = None  # type: ignore

# For Windows COM initialization in TTS worker thread
try:
    import pythoncom
    PYTHONCOM_AVAILABLE = True
except ImportError:
    PYTHONCOM_AVAILABLE = False
    pythoncom = None  # type: ignore


# ─── Premium Dark Palette — Charcoal/Navy with Electric Blue Accents ──────
BG_MAIN       = "#0a0a12"   # Main window - deep charcoal/navy
BG_PANEL      = "#0f0f1a"   # Sidebar/header panels
BG_CARD       = "#141420"   # Cards and conversation area
BG_CARD_HOVER = "#1a1a2a"   # Card hover state
BG_INPUT      = "#181824"   # Input fields
BORDER        = "#2a2a40"   # Subtle borders
BORDER_ACCENT = "#00d4ff"   # Electric blue accent borders

TEXT_PRIMARY  = "#f0f4ff"   # Primary text - bright
TEXT_SECONDARY = "#9ca3c8"  # Secondary text
TEXT_MUTED    = "#6a6f8a"   # Muted text
TEXT_DIM      = "#4a4f6a"   # Dim text

# Electric blue accent system
ELECTRIC_BLUE   = "#00d4ff"  # Primary accent - electric cyan/blue
ELECTRIC_BLUE_GLOW = "#66e8ff" # Lighter glow
ELECTRIC_BLUE_DIM  = "#00a8cc" # Darker variant
ELECTRIC_VIOLET = "#a855f7"   # Secondary accent - violet (for user messages)
ELECTRIC_VIOLET_GLOW = "#c084fc"
ELECTRIC_VIOLET_SOFT = "#d8b4fe" # User message bubbles

SUCCESS      = "#22c55e"
WARNING      = "#f59e0b"
DANGER       = "#ef4444"

ASSISTANT_BG = "#0e1a2a"  # Assistant message background - subtle blue tint
USER_BG      = "#1a0e2a"  # User message background - subtle violet tint


def _hex_lerp(color_a: str, color_b: str, t: float) -> str:
    """Linearly interpolate between two #rrggbb colors (0.0 -> a, 1.0 -> b)."""
    r = int(color_a[1:3], 16) + int((int(color_b[1:3], 16) - int(color_a[1:3], 16)) * t)
    g = int(color_a[3:5], 16) + int((int(color_b[3:5], 16) - int(color_a[3:5], 16)) * t)
    b = int(color_a[5:7], 16) + int((int(color_b[5:7], 16) - int(color_a[5:7], 16)) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


# Voice orb states
ORB_READY = "ready"
ORB_LISTENING = "listening"
ORB_PROCESSING = "processing"
ORB_SPEAKING = "speaking"


class VoiceAssistantApp:
    """Main Tkinter application for the voice assistant."""

    # Voice orb configuration
    ORB_SIZE = 150
    ORB_CENTER = 75
    ORB_RINGS = 5

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("NOVA — Intelligent Voice Assistant")
        self.root.geometry("1300x850")
        self.root.minsize(1000, 680)
        self.root.configure(bg=BG_MAIN)

        # Initialize core logic
        self.assistant = VoiceAssistantCore()

        # Speech recognition components
        self.recognizer: Optional["sr.Recognizer"] = None
        self.microphone: Optional["sr.Microphone"] = None
        self.mic_ok = False
        self.listening = False
        self._stop_event = threading.Event()
        self.listen_thread: Optional[threading.Thread] = None
        self.mic_device_index = None  # Use system default microphone

        # Text-to-speech engine
        self.tts_engine = None
        self.speaking = False
        self._tts_speaking = False
        self.tts_enabled = tk.BooleanVar(value=True)
        self.voice_names: list = []
        self.voice_ids: list = []

        # Thread communication
        self.gui_queue: "queue.Queue[tuple[str, object]]" = queue.Queue()

        # TTS queue and worker thread
        self.tts_queue: "queue.Queue[Optional[str]]" = queue.Queue()
        self.tts_worker_thread: Optional[threading.Thread] = None
        self._tts_shutdown = threading.Event()

        # GUI setup
        self.setup_styles()
        self.create_widgets()
        self.initialize_speech_components()

        # Start queue processor
        self._poll_gui_queue()

        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Welcome message
        self.add_message(
            "NOVA",
            "Hello! I'm NOVA, your intelligent voice assistant. Click the microphone or type a command below. Try 'help' to see what I can do.",
            "assistant",
        )
        self._set_status("Ready")

    # ─── Styling ──────────────────────────────────────────────────────────
    def setup_styles(self):
        """Configure ttk styles for the dark theme."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=BG_MAIN)
        style.configure("Card.TFrame", background=BG_CARD)
        style.configure("Sidebar.TFrame", background=BG_PANEL)
        style.configure("TLabel", background=BG_MAIN, foreground=TEXT_PRIMARY)
        style.configure("Muted.TLabel", background=BG_MAIN, foreground=TEXT_MUTED)
        style.configure("Dim.TLabel", background=BG_MAIN, foreground=TEXT_DIM)
        style.configure("Card.TLabel", background=BG_CARD, foreground=TEXT_PRIMARY)
        style.configure("Card.Muted.TLabel", background=BG_CARD, foreground=TEXT_MUTED)
        style.configure("Card.Dim.TLabel", background=BG_CARD, foreground=TEXT_DIM)
        style.configure("TScale", background=BG_CARD, troughcolor=BORDER, sliderrelief="flat")
        style.map("TScale", background=[("active", BG_CARD)])
        style.configure(
            "TCombobox",
            fieldbackground=BG_INPUT,
            foreground=TEXT_PRIMARY,
            background=BG_INPUT,
            arrowcolor=TEXT_MUTED,
            borderwidth=0,
            relief="flat",
        )
        style.map("TCombobox",
            fieldbackground=[("readonly", BG_INPUT)],
            selectbackground=[("readonly", ELECTRIC_BLUE)],
            selectforeground=[("readonly", "white")],
            borderwidth=[("readonly", 0)],
        )
        style.configure("TCheckbutton", background=BG_CARD, foreground=TEXT_PRIMARY)
        style.map("TCheckbutton",
            background=[("active", BG_CARD)],
            foreground=[("active", TEXT_PRIMARY)],
            indicatorcolor=[("selected", ELECTRIC_BLUE)],
        )

        # Scrollbar styling
        style.configure("Vertical.TScrollbar",
            background=BG_CARD, troughcolor=BG_MAIN, bordercolor=BG_MAIN,
            arrowcolor=TEXT_MUTED, width=10, gripcount=0)
        style.map("Vertical.TScrollbar",
            background=[("active", BG_CARD_HOVER)],
            arrowcolor=[("active", ELECTRIC_BLUE)])

    @staticmethod
    def _hover(widget, base_bg: str, hover_bg: str, base_fg: str = None, hover_fg: str = None):
        """Add hover highlight to any widget."""
        def on_enter(_e):
            widget.configure(bg=hover_bg)
            if hover_fg:
                widget.configure(fg=hover_fg)
        def on_leave(_e):
            widget.configure(bg=base_bg)
            if base_fg:
                widget.configure(fg=base_fg)
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def _card(self, parent, padding=16):
        """Create a dark card frame with a subtle border."""
        frame = tk.Frame(
            parent,
            bg=BG_CARD,
            highlightthickness=1,
            highlightbackground=BORDER,
            padx=padding,
            pady=padding,
        )
        # Hover effect on card
        frame.bind("<Enter>", lambda e: frame.configure(highlightbackground=BORDER_ACCENT))
        frame.bind("<Leave>", lambda e: frame.configure(highlightbackground=BORDER))
        return frame

    def _section_title(self, parent, text):
        """Small uppercase section heading."""
        return tk.Label(
            parent,
            text=text.upper(),
            bg=BG_CARD,
            fg=TEXT_DIM,
            font=("Segoe UI", 7, "bold"),
        )

    def _pill_button(self, parent, text, command, primary=False, compact=True):
        """Create a modern pill-style button."""
        if primary:
            bg, fg = ELECTRIC_BLUE, "white"
            hover_bg, hover_fg = ELECTRIC_BLUE_DIM, "white"
        else:
            bg, fg = BG_INPUT, TEXT_PRIMARY
            hover_bg, hover_fg = BG_CARD_HOVER, ELECTRIC_BLUE

        padx = 16 if compact else 24
        pady = 6 if compact else 10
        font = ("Segoe UI", 9, "bold") if compact else ("Segoe UI", 10, "bold")

        btn = tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=hover_bg, activeforeground=hover_fg,
            font=font, relief="flat", bd=0, padx=padx, pady=pady,
            cursor="hand2",
        )
        self._hover(btn, bg, hover_bg, fg, hover_fg)
        return btn

    def _icon_button(self, parent, text, command, size=40, primary=False):
        """Create a circular icon button."""
        if primary:
            bg, fg = ELECTRIC_BLUE, "white"
            hover_bg = ELECTRIC_BLUE_DIM
        else:
            bg, fg = BG_INPUT, TEXT_MUTED
            hover_bg = BG_CARD_HOVER

        btn = tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=hover_bg, activeforeground="white" if primary else ELECTRIC_BLUE,
            font=("Segoe UI", 14), relief="flat", bd=0,
            width=3, height=1, cursor="hand2",
        )
        self._hover(btn, bg, hover_bg, fg, "white" if primary else ELECTRIC_BLUE)
        return btn

    # ─── Widget Layout ────────────────────────────────────────────────────
    def create_widgets(self):
        """Create and layout all GUI components."""
        # ---- header / hero section ------------------------------------
        hero = tk.Frame(self.root, bg=BG_MAIN)
        hero.pack(side=tk.TOP, fill=tk.X, padx=24, pady=(20, 12))

        # Branding
        brand_wrap = tk.Frame(hero, bg=BG_MAIN)
        brand_wrap.pack(side=tk.LEFT)

        tk.Label(
            brand_wrap,
            text="NOVA",
            bg=BG_MAIN,
            fg=ELECTRIC_BLUE,
            font=("Segoe UI", 32, "bold"),
        ).pack(anchor=tk.W)

        tk.Label(
            brand_wrap,
            text="Intelligent Voice Assistant",
            bg=BG_MAIN,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 13),
        ).pack(anchor=tk.W)

        tk.Label(
            brand_wrap,
            text="OIBSIP · Task 1",
            bg=BG_MAIN,
            fg=TEXT_DIM,
            font=("Segoe UI", 9),
        ).pack(anchor=tk.W, pady=(4, 0))

        # Voice orb canvas (right side of hero)
        self.orb_canvas = tk.Canvas(
            hero,
            width=self.ORB_SIZE,
            height=self.ORB_SIZE,
            bg=BG_MAIN,
            highlightthickness=0,
        )
        self.orb_canvas.pack(side=tk.RIGHT, padx=(0, 8))
        self._build_voice_orb()

        # Orb status label
        self.orb_status = tk.Label(
            hero,
            text="Ready when you are",
            bg=BG_MAIN,
            fg=TEXT_MUTED,
            font=("Segoe UI", 11),
        )
        self.orb_status.pack(side=tk.RIGHT, padx=(0, 16), pady=(0, 8), anchor=tk.S)

        # ---- body: conversation (left) + sidebar (right) ----
        body = tk.Frame(self.root, bg=BG_MAIN)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=24, pady=(0, 12))

        left = tk.Frame(body, bg=BG_MAIN)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        sidebar = tk.Frame(body, bg=BG_MAIN, width=320)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        sidebar.pack_propagate(False)

        self._build_conversation(left)
        self._build_composer(left)
        self._build_sidebar(sidebar)

        # ---- bottom status bar ----------------------------------------
        status_bar = tk.Frame(self.root, bg=BG_PANEL, height=36)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        status_bar.pack_propagate(False)

        self.status_label = tk.Label(
            status_bar,
            text="Ready",
            bg=BG_PANEL,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
            anchor=tk.W,
        )
        self.status_label.pack(side=tk.LEFT, padx=20)

        self.engine_label = tk.Label(
            status_bar,
            text="Microphone: Checking…  •  Voice: Checking…",
            bg=BG_PANEL,
            fg=TEXT_DIM,
            font=("Segoe UI", 9),
            anchor=tk.E,
        )
        self.engine_label.pack(side=tk.RIGHT, padx=20)

    def _build_voice_orb(self):
        """Create the premium AI voice orb using layered circles/rings."""
        c = self.orb_canvas
        center = self.ORB_CENTER
        max_r = self.ORB_CENTER - 4

        # Store ring IDs for animation
        self.orb_rings = []
        self.orb_ring_phases = [0.0] * self.ORB_RINGS
        self.orb_ring_base_radii = []
        self.orb_glow_rings = []

        # Base glow rings (static backdrop)
        for i in range(4):
            r = max_r - i * 8
            glow = c.create_oval(
                center - r, center - r, center + r, center + r,
                outline="", fill="",
            )
            self.orb_glow_rings.append(glow)

        # Animated rings
        for i in range(self.ORB_RINGS):
            r = max_r - i * 12 - 4
            self.orb_ring_base_radii.append(r)
            ring = c.create_oval(
                center - r, center - r, center + r, center + r,
                outline=ELECTRIC_BLUE if i % 2 == 0 else ELECTRIC_VIOLET,
                width=2 if i < 2 else 1,
            )
            self.orb_rings.append(ring)

        # Central core
        core_r = 20
        self.orb_core = c.create_oval(
            center - core_r, center - core_r, center + core_r, center + core_r,
            fill=ELECTRIC_BLUE, outline="",
        )
        # Core inner glow
        self.orb_core_glow = c.create_oval(
            center - core_r + 4, center - core_r + 4,
            center + core_r - 4, center + core_r - 4,
            outline=ELECTRIC_BLUE_GLOW, width=2,
        )

        # Initialize orb state
        self.orb_state = ORB_READY
        self.orb_animation_id = None
        self._start_orb_animation()

    def _start_orb_animation(self):
        """Start the orb animation loop."""
        self._animate_orb()

    def _animate_orb(self):
        """Animate the voice orb based on current state."""
        c = self.orb_canvas
        center = self.ORB_CENTER
        max_r = self.ORB_CENTER - 4
        import math

        if self.orb_state == ORB_READY:
            # Calm breathing - slow pulsing electric blue glow
            phase = (self.orb_ring_phases[0] + 0.02) % (2 * math.pi)
            for i in range(self.ORB_RINGS):
                self.orb_ring_phases[i] = phase + i * 0.8
                r = self.orb_ring_base_radii[i] + math.sin(self.orb_ring_phases[i]) * 3
                c.coords(self.orb_rings[i],
                    center - r, center - r, center + r, center + r)
                color = ELECTRIC_BLUE if i % 2 == 0 else ELECTRIC_VIOLET
                c.itemconfig(self.orb_rings[i], outline=color, width=2 if i < 2 else 1)

            # Core gentle pulse
            core_pulse = 20 + math.sin(phase * 0.5) * 3
            c.coords(self.orb_core,
                center - core_pulse, center - core_pulse,
                center + core_pulse, center + core_pulse)
            c.itemconfig(self.orb_core, fill=ELECTRIC_BLUE)
            c.itemconfig(self.orb_core_glow, outline=ELECTRIC_BLUE_GLOW)

            # Subtle glow rings
            for i, glow in enumerate(self.orb_glow_rings):
                gr = max_r - i * 8 + math.sin(phase + i) * 4
                c.coords(glow, center - gr, center - gr, center + gr, center + gr)
                c.itemconfig(glow, fill=_hex_lerp(BG_MAIN, ELECTRIC_BLUE, 0.04), outline="")

        elif self.orb_state == ORB_LISTENING:
            # Expanded/pulsing rings - active listening (electric blue dominant)
            phase = (self.orb_ring_phases[0] + 0.15) % (2 * math.pi)
            for i in range(self.ORB_RINGS):
                self.orb_ring_phases[i] = phase + i * 0.5
                expand = (math.sin(self.orb_ring_phases[i]) + 1) * 0.5
                r = self.orb_ring_base_radii[i] + 8 + expand * 18
                c.coords(self.orb_rings[i],
                    center - r, center - r, center + r, center + r)
                color = ELECTRIC_BLUE if i % 2 == 0 else ELECTRIC_BLUE_GLOW
                c.itemconfig(self.orb_rings[i], outline=color, width=3 if i < 2 else 2)

            # Core expands and glows electric blue
            core_pulse = 24 + math.sin(phase * 2) * 8
            c.coords(self.orb_core,
                center - core_pulse, center - core_pulse,
                center + core_pulse, center + core_pulse)
            c.itemconfig(self.orb_core, fill=ELECTRIC_BLUE)
            c.itemconfig(self.orb_core_glow, outline=ELECTRIC_BLUE_GLOW, width=3)

            # Glow rings active
            for i, glow in enumerate(self.orb_glow_rings):
                gr = max_r - i * 8 + math.sin(phase + i * 0.7) * 10
                c.coords(glow, center - gr, center - gr, center + gr, center + gr)
                c.itemconfig(glow, fill=_hex_lerp(BG_MAIN, ELECTRIC_BLUE, 0.12), outline="")

        elif self.orb_state == ORB_PROCESSING:
            # Rotating/alternating rings - thinking
            phase = (self.orb_ring_phases[0] + 0.12) % (2 * math.pi)
            for i in range(self.ORB_RINGS):
                self.orb_ring_phases[i] = phase + i * 1.2
                r = self.orb_ring_base_radii[i] + math.sin(self.orb_ring_phases[i]) * 5
                c.coords(self.orb_rings[i],
                    center - r, center - r, center + r, center + r)
                color = ELECTRIC_BLUE if int(phase * 2 + i) % 2 == 0 else ELECTRIC_VIOLET
                c.itemconfig(self.orb_rings[i], outline=color, width=2)

            # Core spins with gradient feel
            core_pulse = 22 + math.sin(phase * 3) * 4
            c.coords(self.orb_core,
                center - core_pulse, center - core_pulse,
                center + core_pulse, center + core_pulse)
            color = ELECTRIC_BLUE if int(phase * 3) % 2 == 0 else ELECTRIC_VIOLET
            c.itemconfig(self.orb_core, fill=color)
            c.itemconfig(self.orb_core_glow, outline=color)

        elif self.orb_state == ORB_SPEAKING:
            # Waveform-like ring activity
            phase = (self.orb_ring_phases[0] + 0.18) % (2 * math.pi)
            for i in range(self.ORB_RINGS):
                self.orb_ring_phases[i] = phase + i * 0.4
                wave = abs(math.sin(self.orb_ring_phases[i] * 2))
                r = self.orb_ring_base_radii[i] + wave * 14
                c.coords(self.orb_rings[i],
                    center - r, center - r, center + r, center + r)
                color = ELECTRIC_BLUE if i % 2 == 0 else ELECTRIC_VIOLET
                c.itemconfig(self.orb_rings[i], outline=color, width=2 + int(wave * 2))

            # Core pulses with speech rhythm
            core_pulse = 22 + abs(math.sin(phase * 4)) * 10
            c.coords(self.orb_core,
                center - core_pulse, center - core_pulse,
                center + core_pulse, center + core_pulse)
            c.itemconfig(self.orb_core, fill=ELECTRIC_BLUE)
            c.itemconfig(self.orb_core_glow, outline=ELECTRIC_BLUE_GLOW, width=3)

        self.orb_animation_id = self.root.after(40, self._animate_orb)

    def _set_orb_state(self, state: str, status_text: str = None):
        """Update the orb visual state and status text."""
        self.orb_state = state
        if status_text:
            self.orb_status.configure(text=status_text, fg=TEXT_PRIMARY)
        elif state == ORB_READY:
            self.orb_status.configure(text="Ready when you are", fg=TEXT_MUTED)
        elif state == ORB_LISTENING:
            self.orb_status.configure(text="Listening…", fg=ELECTRIC_BLUE)
        elif state == ORB_PROCESSING:
            self.orb_status.configure(text="Processing…", fg=ELECTRIC_VIOLET)
        elif state == ORB_SPEAKING:
            self.orb_status.configure(text="Speaking…", fg=ELECTRIC_BLUE_GLOW)

    def _build_visualizer(self):
        """Legacy visualizer - kept for compatibility but not used."""
        pass

    def _build_conversation(self, parent):
        """Conversation history area with modern chat-style messages."""
        conv_card = self._card(parent, padding=0)
        conv_card.pack(fill=tk.BOTH, expand=True)

        self.conversation = scrolledtext.ScrolledText(
            conv_card,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            state="disabled",
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            insertbackground=ELECTRIC_BLUE,
            selectbackground=ELECTRIC_BLUE,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            padx=18,
            pady=14,
        )
        self.conversation.pack(fill=tk.BOTH, expand=True)

        # Modern chat-style tags with card/bubble feel
        # User messages - right aligned with violet accent
        self.conversation.tag_configure(
            "user_name", foreground=ELECTRIC_VIOLET, justify="right",
            font=("Segoe UI", 7, "bold"), spacing1=8, spacing3=2,
        )
        self.conversation.tag_configure(
            "user", foreground=ELECTRIC_VIOLET_SOFT, justify="right",
            font=("Segoe UI", 10), spacing3=16, lmargin1=60, lmargin2=60, rmargin=12,
        )
        # Assistant messages - left aligned with electric blue accent
        self.conversation.tag_configure(
            "assistant_name", foreground=ELECTRIC_BLUE, justify="left",
            font=("Segoe UI", 7, "bold"), spacing1=8, spacing3=2,
        )
        self.conversation.tag_configure(
            "assistant", foreground="#c8e8ff", justify="left",
            font=("Segoe UI", 10), spacing3=16, lmargin1=12, lmargin2=12, rmargin=60,
        )
        # System messages
        self.conversation.tag_configure(
            "system", foreground=TEXT_DIM, justify="center",
            font=("Segoe UI", 9, "italic"), spacing1=6, spacing3=6,
        )
        # Timestamp
        self.conversation.tag_configure(
            "timestamp", foreground=TEXT_DIM, justify="right",
            font=("Segoe UI", 7), spacing3=0,
        )

    def _build_composer(self, parent):
        """Modern input composer: Ask NOVA anything... + SEND + MIC + CLEAR."""
        composer = tk.Frame(parent, bg=BG_MAIN)
        composer.pack(fill=tk.X, pady=(16, 0))

        # Input container with integrated buttons
        input_wrap = tk.Frame(composer, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER)
        input_wrap.pack(fill=tk.X)
        input_wrap.bind("<Enter>", lambda e: input_wrap.configure(highlightbackground=BORDER_ACCENT))
        input_wrap.bind("<Leave>", lambda e: input_wrap.configure(highlightbackground=BORDER))

        # Main text entry
        self.text_entry = tk.Entry(
            input_wrap,
            font=("Segoe UI", 12),
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            insertbackground=ELECTRIC_BLUE,
            relief="flat",
            bd=0,
            highlightthickness=0,
        )
        self.text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(20, 12), pady=14, ipady=4)
        self.text_entry.bind("<Return>", lambda _e: self.send_text_command())
        # Placeholder behavior
        self._placeholder_text = "Ask NOVA anything…"
        self.text_entry.insert(0, self._placeholder_text)
        self.text_entry.configure(fg=TEXT_DIM)
        self.text_entry.bind("<FocusIn>", self._on_entry_focus_in)
        self.text_entry.bind("<FocusOut>", self._on_entry_focus_out)

        # Action buttons inside the composer
        btn_frame = tk.Frame(input_wrap, bg=BG_CARD)
        btn_frame.pack(side=tk.RIGHT, padx=(0, 16), pady=8)

        # Microphone button (primary - circular with electric blue)
        self.listen_button = tk.Button(
            btn_frame, text="●", command=self.toggle_listening,
            bg=ELECTRIC_BLUE, fg="white", activebackground=ELECTRIC_BLUE_DIM, activeforeground="white",
            font=("Segoe UI", 16, "bold"), relief="flat", bd=0,
            width=3, height=1, cursor="hand2",
        )
        self.listen_button.pack(side=tk.LEFT, padx=(0, 8))
        self._hover(self.listen_button, ELECTRIC_BLUE, ELECTRIC_BLUE_DIM)
        self._listen_button_primary = True

        # Send button
        self.send_button = tk.Button(
            btn_frame, text="SEND", command=self.send_text_command,
            bg=ELECTRIC_BLUE, fg="white", activebackground=ELECTRIC_BLUE_DIM, activeforeground="white",
            font=("Segoe UI", 9, "bold"), relief="flat", bd=0, padx=18, pady=8,
            cursor="hand2",
        )
        self.send_button.pack(side=tk.LEFT, padx=(0, 8))
        self._hover(self.send_button, ELECTRIC_BLUE, ELECTRIC_BLUE_DIM)

        # Clear button (secondary)
        self.clear_button = tk.Button(
            btn_frame, text="CLEAR", command=self.clear_conversation,
            bg=BG_INPUT, fg=TEXT_MUTED, activebackground=BG_CARD_HOVER, activeforeground=ELECTRIC_BLUE,
            font=("Segoe UI", 9), relief="flat", bd=0, padx=14, pady=8,
            cursor="hand2",
        )
        self.clear_button.pack(side=tk.LEFT)
        self._hover(self.clear_button, BG_INPUT, BG_CARD_HOVER, TEXT_MUTED, ELECTRIC_BLUE)

    def _on_entry_focus_in(self, event):
        """Handle entry focus in - clear placeholder."""
        if self.text_entry.get() == self._placeholder_text:
            self.text_entry.delete(0, tk.END)
            self.text_entry.configure(fg=TEXT_PRIMARY)

    def _on_entry_focus_out(self, event):
        """Handle entry focus out - restore placeholder if empty."""
        if not self.text_entry.get().strip():
            self.text_entry.insert(0, self._placeholder_text)
            self.text_entry.configure(fg=TEXT_DIM)

    def _build_sidebar(self, parent):
        """Right-hand System panel: mic/voice status + quick actions."""
        # ---- System status card ----
        sys_card = self._card(parent)
        sys_card.pack(fill=tk.X, pady=(0, 12))

        # System header
        header_frame = tk.Frame(sys_card, bg=BG_CARD)
        header_frame.pack(fill=tk.X, pady=(0, 12))

        tk.Label(
            header_frame, text="⚙ SYSTEM", bg=BG_CARD, fg=TEXT_DIM,
            font=("Segoe UI", 7, "bold"),
        ).pack(side=tk.LEFT)

        # Status indicators
        status_grid = tk.Frame(sys_card, bg=BG_CARD)
        status_grid.pack(fill=tk.X, pady=(0, 8))

        # Microphone status
        mic_row = tk.Frame(status_grid, bg=BG_CARD)
        mic_row.pack(fill=tk.X, pady=4)
        self.mic_status_dot = tk.Label(
            mic_row, text="●", bg=BG_CARD, fg=WARNING,
            font=("Segoe UI", 10),
        )
        self.mic_status_dot.pack(side=tk.LEFT)
        self.mic_status_label = tk.Label(
            mic_row, text="Microphone: Checking…", bg=BG_CARD, fg=TEXT_MUTED,
            font=("Segoe UI", 9), anchor=tk.W,
        )
        self.mic_status_label.pack(side=tk.LEFT, padx=(8, 0), fill=tk.X, expand=True)

        # Voice output status
        voice_row = tk.Frame(status_grid, bg=BG_CARD)
        voice_row.pack(fill=tk.X, pady=4)
        self.voice_status_dot = tk.Label(
            voice_row, text="●", bg=BG_CARD, fg=WARNING,
            font=("Segoe UI", 10),
        )
        self.voice_status_dot.pack(side=tk.LEFT)
        self.voice_status_label = tk.Label(
            voice_row, text="Voice Output: Checking…", bg=BG_CARD, fg=TEXT_MUTED,
            font=("Segoe UI", 9), anchor=tk.W,
        )
        self.voice_status_label.pack(side=tk.LEFT, padx=(8, 0), fill=tk.X, expand=True)

        # Divider
        divider = tk.Frame(sys_card, bg=BORDER, height=1)
        divider.pack(fill=tk.X, pady=10)

        # Controls
        controls_frame = tk.Frame(sys_card, bg=BG_CARD)
        controls_frame.pack(fill=tk.X)

        # TTS enable
        self.tts_check = tk.Checkbutton(
            controls_frame, text="Voice responses",
            variable=self.tts_enabled, command=self._on_tts_toggled,
            bg=BG_CARD, fg=TEXT_PRIMARY, selectcolor=BG_INPUT,
            activebackground=BG_CARD, activeforeground=TEXT_PRIMARY,
            font=("Segoe UI", 9),
        )
        self.tts_check.pack(anchor=tk.W, pady=2)

        # Voice selector
        tk.Label(
            controls_frame, text="Voice", bg=BG_CARD, fg=TEXT_DIM,
            font=("Segoe UI", 7, "bold"),
        ).pack(anchor=tk.W, pady=(8, 2))
        self.voice_combo = ttk.Combobox(
            controls_frame, state="readonly", width=30, font=("Segoe UI", 9),
        )
        self.voice_combo.pack(anchor=tk.W, fill=tk.X)
        self.voice_combo.bind("<<ComboboxSelected>>", self._on_voice_selected)

        # Speech rate
        tk.Label(
            controls_frame, text="Speech rate", bg=BG_CARD, fg=TEXT_DIM,
            font=("Segoe UI", 7, "bold"),
        ).pack(anchor=tk.W, pady=(8, 2))
        rate_frame = tk.Frame(controls_frame, bg=BG_CARD)
        rate_frame.pack(fill=tk.X)
        self.rate_scale = ttk.Scale(
            rate_frame, from_=100, to=300, value=180,
            command=self._on_rate_changed,
        )
        self.rate_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.rate_value_label = tk.Label(
            rate_frame, text="180 wpm", bg=BG_CARD, fg=TEXT_MUTED,
            font=("Segoe UI", 8), width=8, anchor=tk.E,
        )
        self.rate_value_label.pack(side=tk.LEFT, padx=(8, 0))

        # Volume
        tk.Label(
            controls_frame, text="Volume", bg=BG_CARD, fg=TEXT_DIM,
            font=("Segoe UI", 7, "bold"),
        ).pack(anchor=tk.W, pady=(8, 2))
        vol_frame = tk.Frame(controls_frame, bg=BG_CARD)
        vol_frame.pack(fill=tk.X)
        self.volume_scale = ttk.Scale(
            vol_frame, from_=0.0, to=1.0, value=0.9,
            command=self._on_volume_changed,
        )
        self.volume_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.volume_value_label = tk.Label(
            vol_frame, text="90%", bg=BG_CARD, fg=TEXT_MUTED,
            font=("Segoe UI", 8), width=6, anchor=tk.E,
        )
        self.volume_value_label.pack(side=tk.LEFT, padx=(8, 0))

        # Retry microphone button
        self.retry_mic_button = self._pill_button(
            controls_frame, "Retry Microphone", self._init_microphone,
            primary=False, compact=True,
        )
        self.retry_mic_button.pack(fill=tk.X, pady=(12, 0))

        # ---- Quick Actions card ----
        quick_card = self._card(parent)
        quick_card.pack(fill=tk.X)

        tk.Label(
            quick_card, text="QUICK ACTIONS", bg=BG_CARD, fg=TEXT_DIM,
            font=("Segoe UI", 7, "bold"),
        ).pack(anchor=tk.W, pady=(0, 10))

        quick_commands = [
            ("⏰", "Time", "what time is it"),
            ("📅", "Date", "what's today's date"),
            ("😄", "Joke", "tell me a joke"),
            ("🔍", "Google", "open google"),
            ("▶", "YouTube", "open youtube"),
            ("💻", "GitHub", "open github"),
        ]

        pills_frame = tk.Frame(quick_card, bg=BG_CARD)
        pills_frame.pack(fill=tk.X)

        for i, (icon, label, command) in enumerate(quick_commands):
            row = i // 2
            col = i % 2
            pill = tk.Frame(pills_frame, bg=BG_INPUT, highlightthickness=1, highlightbackground=BORDER)
            pill.grid(row=row, column=col, padx=(0 if col == 0 else 6, 0), pady=(0, 6), sticky="ew")
            pills_frame.grid_columnconfigure(col, weight=1)

            pill.bind("<Enter>", lambda e, p=pill: p.configure(highlightbackground=ELECTRIC_BLUE, bg=BG_CARD_HOVER))
            pill.bind("<Leave>", lambda e, p=pill: p.configure(highlightbackground=BORDER, bg=BG_INPUT))

            btn = tk.Button(
                pill, text=f"{icon}  {label}", command=lambda c=command: self._quick_send(c),
                bg=BG_INPUT, fg=TEXT_PRIMARY, activebackground=BG_CARD_HOVER, activeforeground=ELECTRIC_BLUE,
                font=("Segoe UI", 9), relief="flat", bd=0, padx=12, pady=8,
                cursor="hand2", anchor=tk.W,
            )
            btn.pack(fill=tk.X, padx=2, pady=2)
            btn.bind("<Enter>", lambda e, p=pill: p.configure(highlightbackground=ELECTRIC_BLUE, bg=BG_CARD_HOVER))
            btn.bind("<Leave>", lambda e, p=pill: p.configure(highlightbackground=BORDER, bg=BG_INPUT))

    # ─── Speech Component Initialization ─────────────────────────────────
    def initialize_speech_components(self):
        """Initialize speech recognition and TTS engines."""
        self._init_microphone()
        self._init_tts()
        self._refresh_engine_label()

    def _init_microphone(self):
        """(Re)initialize the microphone; safe to call again on failure.

        Uses system default microphone (device_index=None). Falls back gracefully
        with clear error messages if initialization fails.
        """
        print("[MIC] Initializing microphone...")
        self.mic_ok = False
        if not SPEECH_RECOGNITION_AVAILABLE:
            self._set_mic_status(
                "SpeechRecognition is not installed. Typed commands still work. "
                "See requirements.txt."
            )
            self._refresh_mic_ui()
            return
        try:
            if self.recognizer is None:
                self.recognizer = sr.Recognizer()
            # Optimized recognizer settings for reliable recognition
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.recognizer.phrase_threshold = 0.3
            self.recognizer.non_speaking_duration = 0.5

            # Use system default microphone
            print("[MIC] Creating microphone with default device...")
            self.microphone = sr.Microphone(device_index=self.mic_device_index)
            print("[MIC] Microphone object created")
            with self.microphone as source:
                print("[MIC] Adjusting for ambient noise (1.0s)...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                print(f"[MIC] Energy threshold after calibration: {self.recognizer.energy_threshold}")
            self.mic_ok = True
            print("[MIC] Microphone ready")
            self._set_mic_status(
                "Microphone ready (default device). Click LISTEN and speak."
            )
        except Exception as exc:
            print(f"[MIC ERROR] {type(exc).__name__}: {exc}")
            self.mic_ok = False
            # Provide specific guidance for common PortAudio errors
            error_msg = str(exc)
            if "Unanticipated host error" in error_msg or "Errno -9999" in error_msg:
                self._set_mic_status(
                    "Microphone unavailable (audio driver error). "
                    "Check microphone permissions/privacy settings. "
                    "Typed commands still work — use RETRY MICROPHONE to re-attempt."
                )
            else:
                self._set_mic_status(
                    f"Microphone unavailable: {exc}. "
                    "Install PyAudio (see README) or use typed commands."
                )
        finally:
            self._refresh_mic_ui()
            self._refresh_engine_label()

    def _init_tts(self):
        """Initialize TTS: discover voices on main thread, start worker thread.

        The actual pyttsx3 engine is created inside the worker thread
        (with COM initialization) to avoid SAPI5 cross-threading issues.
        """
        self.tts_engine = None
        self.voice_names = []
        self.voice_ids = []
        self._tts_shutdown.clear()
        if not TTS_AVAILABLE:
            self._set_tts_status(
                "pyttsx3 is not installed. The assistant will reply in text only. "
                "See requirements.txt."
            )
            self._refresh_engine_label()
            return
        try:
            # Create a temporary engine on main thread just to enumerate voices
            temp_engine = pyttsx3.init()
            voices = temp_engine.getProperty("voices") or []
            self.voice_names = [v.name for v in voices]
            self.voice_ids = [v.id for v in voices]
            temp_engine.stop()
            del temp_engine

            # Prefer a clearly female voice when one exists, else the first.
            preferred = None
            for i, name in enumerate(self.voice_names):
                name_lower = name.lower()
                if "female" in name_lower or "zira" in name_lower or "samantha" in name_lower:
                    preferred = i
                    break
            if preferred is None and self.voice_names:
                preferred = 0

            if self.voice_names:
                self.voice_combo["values"] = self.voice_names
                self.voice_combo.current(preferred or 0)
            else:
                self.voice_combo["values"] = ["System default"]
                self.voice_combo.current(0)

            self._set_tts_status(
                f"Voice output ready — {len(self.voice_names)} voice(s) available."
            )

            # Start the persistent TTS worker thread (creates its own engine)
            self.tts_worker_thread = threading.Thread(
                target=self._tts_worker_loop, name="tts-worker", daemon=True
            )
            self.tts_worker_thread.start()

        except Exception as exc:
            self.tts_engine = None
            self._set_tts_status(f"Voice output error: {exc}. Text replies only.")
        finally:
            self._refresh_engine_label()

    def _refresh_mic_ui(self):
        """Sync the listen button and mic status dot with mic state."""
        if self.listening:
            return
        if hasattr(self, 'mic_status_dot') and hasattr(self, 'mic_status_label'):
            if self.mic_ok:
                self.mic_status_dot.configure(fg=SUCCESS)
                self.mic_status_label.configure(text="Microphone: Ready", fg=TEXT_MUTED)
            elif not SPEECH_RECOGNITION_AVAILABLE:
                self.mic_status_dot.configure(fg=TEXT_DIM)
                self.mic_status_label.configure(text="Microphone: Not installed", fg=TEXT_DIM)
            else:
                self.mic_status_dot.configure(fg=DANGER)
                self.mic_status_label.configure(text="Microphone: Unavailable", fg=TEXT_MUTED)
        if hasattr(self, 'listen_button'):
            self.listen_button.configure(state=tk.NORMAL if self.mic_ok else tk.DISABLED)

    def _refresh_engine_label(self):
        """Update the bottom-right engine summary."""
        mic_text = "Ready" if self.mic_ok else "Unavailable"
        voice_ok = TTS_AVAILABLE and self.tts_worker_thread and self.tts_worker_thread.is_alive()
        voice_text = "Ready" if voice_ok else "Unavailable"
        self.engine_label.configure(text=f"Microphone: {mic_text}  •  Voice: {voice_text}")

    # ─── Status + Queue Plumbing ──────────────────────────────────────────
    def _set_status(self, message: str):
        """Update the status bar and orb status (main thread only)."""
        self.status_label.configure(text=message)
        if hasattr(self, 'orb_status'):
            self.orb_status.configure(text=message)

    def _set_mic_status(self, message: str):
        if hasattr(self, 'mic_status_label'):
            self.mic_status_label.configure(text=message)
        self._set_status(message)

    def _set_tts_status(self, message: str):
        if hasattr(self, 'voice_status_label'):
            self.voice_status_label.configure(text=message)

    def _poll_gui_queue(self):
        """Drain the GUI queue and apply every pending update."""
        try:
            while True:
                msg_type, data = self.gui_queue.get_nowait()
                if msg_type == "status":
                    self._set_status(str(data))
                elif msg_type == "user_input":
                    self.add_message("You", str(data), "user")
                elif msg_type == "assistant_response":
                    self.add_message("Assistant", str(data), "assistant")
                    self.speak_text(str(data))
                elif msg_type == "action":
                    self.handle_action(data)
                elif msg_type == "listening_state":
                    self._reset_listening_ui()
                elif msg_type == "speaking_state":
                    if data:
                        self._set_status("Speaking…")
                        self._set_orb_state(ORB_SPEAKING, "Speaking…")
                    elif self.listening:
                        self._set_status("Listening… speak now")
                        self._set_orb_state(ORB_LISTENING, "Listening…")
                    else:
                        self._set_status("Ready")
                        self._set_orb_state(ORB_READY, "Ready when you are")
                self.gui_queue.task_done()
        except queue.Empty:
            pass
        self.root.after(60, self._poll_gui_queue)

    # ─── Conversation Display ─────────────────────────────────────────────
    def add_message(self, speaker: str, text: str, kind: str):
        """Append a chat-style message (main thread only)."""
        self.conversation.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M")
        display_name = "YOU" if kind == "user" else "NOVA"
        self.conversation.insert(tk.END, f"{display_name}  ·  {timestamp}\n", f"{kind}_name")
        self.conversation.insert(tk.END, f"{text}\n\n", kind)
        self.conversation.see(tk.END)
        self.conversation.configure(state="disabled")

    def clear_conversation(self):
        """Wipe the conversation history."""
        self.conversation.configure(state="normal")
        self.conversation.delete("1.0", tk.END)
        self.conversation.configure(state="disabled")

    def send_text_command(self):
        """Handle text input from the entry field."""
        user_input = self.text_entry.get().strip()
        if not user_input:
            return
        self.text_entry.delete(0, tk.END)
        self.add_message("You", user_input, "user")
        self._dispatch_command(user_input)

    def _quick_send(self, command: str):
        """Send one of the sidebar's quick commands."""
        self.add_message("You", command, "user")
        self._dispatch_command(command)

    def _dispatch_command(self, user_input: str):
        """Run a command through the core and render the result."""
        try:
            response = self.assistant.process_command(user_input)
        except Exception as exc:
            response = AssistantResponse(text=f"Something went wrong: {exc}")
        self.add_message("Assistant", response.text, "assistant")
        self.speak_text(response.text)
        if response.action:
            self.handle_action({
                "action": response.action,
                "data": response.action_data or {},
            })

    # ─── Listening (Speech Recognition) ──────────────────────────────────
    def toggle_listening(self):
        """Toggle listening state."""
        if self.listening:
            self.stop_listening()
        else:
            self.start_listening()

    def start_listening(self):
        """Start listening for speech input in a background thread."""
        if not SPEECH_RECOGNITION_AVAILABLE or not self.recognizer or not self.microphone:
            messagebox.showwarning(
                "Microphone Unavailable",
                "Speech recognition is not available. Please install "
                "SpeechRecognition and PyAudio, or use the text input instead.",
            )
            return
        if not self.mic_ok:
            messagebox.showwarning(
                "Microphone Not Ready",
                "Microphone initialization failed. Click 'Retry Microphone' "
                "in the System panel to re-attempt, or use text input.",
            )
            return
        if self.listening:
            return

        self.listening = True
        self._stop_event.clear()
        # Update listen button to show stop state
        self.listen_button.configure(text="■", bg=DANGER, activebackground="#dc2626")
        self._listen_button_primary = False
        self._set_status("Listening… speak now")
        self._set_orb_state(ORB_LISTENING, "Listening…")
        self._refresh_engine_label()

        self.listen_thread = threading.Thread(
            target=self.listen_loop, name="mic-listener", daemon=True,
        )
        self.listen_thread.start()

    def stop_listening(self):
        """User-initiated stop: signal the worker, join briefly, reset UI."""
        self.listening = False
        self._stop_event.set()
        thread = self.listen_thread
        if thread and thread.is_alive():
            thread.join(timeout=1.5)
        self._reset_listening_ui()

    def _reset_listening_ui(self):
        """Return the listen controls to their idle state (main thread only)."""
        self.listening = False
        self.listen_button.configure(
            text="●", bg=ELECTRIC_BLUE, activebackground=ELECTRIC_BLUE_DIM,
            state=tk.NORMAL if self.mic_ok else tk.DISABLED,
        )
        self._listen_button_primary = True
        self._set_status("Ready")
        self._set_orb_state(ORB_READY, "Ready when you are")
        self._refresh_engine_label()

    def listen_loop(self):
        """Background thread: capture audio, recognize, queue results.

        Waits for TTS to finish before listening to avoid audio feedback.
        Never touches Tkinter directly — everything goes through gui_queue.
        """
        print("[MIC] listen requested")
        print(f"[MIC] device={self.mic_device_index}")

        while self.listening and not self._stop_event.is_set():
            # Wait for any ongoing TTS to finish before listening
            while self.tts_queue.qsize() > 0 or self._tts_speaking:
                time.sleep(0.1)
                if not self.listening or self._stop_event.is_set():
                    break

            if not self.listening or self._stop_event.is_set():
                break

            try:
                print("[MIC] microphone opened")
                with self.microphone as source:
                    print("[MIC] listening")
                    audio = self.recognizer.listen(
                        source, timeout=5.0, phrase_time_limit=8.0,
                    )
                print("[MIC] audio captured")
            except sr.WaitTimeoutError:
                self.gui_queue.put(("status", "Listening... (no speech detected)"))
                continue
            except AttributeError as exc:
                # Workaround for SpeechRecognition 3.17.0 bug:
                # Microphone.__enter__ can fail silently (stream=None), then __exit__ crashes
                # with "AttributeError: 'NoneType' object has no attribute 'close'"
                if "'NoneType' object has no attribute 'close'" in str(exc):
                    print(f"[MIC ERROR] SpeechRecognition bug detected: {exc}")
                    self.gui_queue.put((
                        "status",
                        "Microphone stream error (driver/permissions?). "
                        "Click 'Retry Microphone' to reinitialize."
                    ))
                else:
                    print(f"[MIC ERROR] {type(exc).__name__}: {exc}")
                    self.gui_queue.put(("status", f"Microphone error: {exc}"))
                break
            except Exception as exc:
                print(f"[MIC ERROR] {type(exc).__name__}: {exc}")
                self.gui_queue.put(("status", f"Microphone error: {exc}"))
                break

            print("[MIC] recognizing")
            self.gui_queue.put(("status", "Recognizing..."))
            try:
                text = self.recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                print("[MIC ERROR] UnknownValueError: Could not understand audio")
                self.gui_queue.put(("status", "Didn't catch that — still listening"))
                continue
            except sr.RequestError as exc:
                print(f"[MIC ERROR] RequestError: {exc}")
                self.gui_queue.put(("status", f"Speech service unreachable: {exc}"))
                continue
            except Exception as exc:
                print(f"[MIC ERROR] {type(exc).__name__}: {exc}")
                self.gui_queue.put(("status", f"Recognition error: {exc}"))
                continue

            if not text:
                continue

            print(f"[MIC] recognized: {text}")
            self.gui_queue.put(("user_input", text))
            try:
                response = self.assistant.process_command(text)
            except Exception as exc:
                self.gui_queue.put(("assistant_response", f"Something went wrong: {exc}"))
                continue
            self.gui_queue.put(("assistant_response", response.text))
            if response.action:
                self.gui_queue.put(("action", {
                    "action": response.action,
                    "data": response.action_data or {},
                }))

        if self.listening:
            self.gui_queue.put(("listening_state", False))

    # ─── Text-to-Speech ───────────────────────────────────────────────────
    def speak_text(self, text: str):
        """Speak text using the TTS engine (queued from any thread)."""
        if not self.tts_enabled.get():
            print(f"[TTS] TTS disabled, skipping: {text}")
            return
        print(f"[TTS] queued: {text}")
        self.tts_queue.put(text)

    def _tts_worker_loop(self):
        """Persistent TTS worker: dequeues and speaks requests sequentially."""
        print(f"[TTS] Worker thread started, alive: {threading.current_thread().is_alive()}")
        if PYTHONCOM_AVAILABLE:
            try:
                pythoncom.CoInitialize()
                print("[TTS] COM initialized")
            except Exception as exc:
                print(f"[TTS ERROR] COM init failed: {type(exc).__name__}: {exc}")
                pass

        engine = None
        if TTS_AVAILABLE:
            try:
                engine = pyttsx3.init("sapi5")
                engine.setProperty("rate", 180)
                engine.setProperty("volume", 0.9)
                print(f"[TTS] Engine created on worker thread")
            except Exception as exc:
                print(f"[TTS ERROR] Engine creation failed: {type(exc).__name__}: {exc}")
                self.gui_queue.put(("status", f"TTS engine creation failed: {exc}"))
                engine = None

        preferred_voice_idx = 0
        if self.voice_ids:
            for i, name in enumerate(self.voice_names):
                name_lower = name.lower()
                if "female" in name_lower or "zira" in name_lower or "samantha" in name_lower:
                    preferred_voice_idx = i
                    break

        if engine and self.voice_ids and preferred_voice_idx < len(self.voice_ids):
            try:
                engine.setProperty("voice", self.voice_ids[preferred_voice_idx])
            except Exception as exc:
                print(f"[TTS ERROR] Voice setProperty failed: {type(exc).__name__}: {exc}")
                pass

        self._worker_engine = engine

        try:
            while not self._tts_shutdown.is_set():
                try:
                    item = self.tts_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                if item is None:
                    print("[TTS] Sentinel received, shutting down worker")
                    self.tts_queue.task_done()
                    break

                if not engine:
                    print("[TTS] No engine available, skipping item")
                    self.tts_queue.task_done()
                    continue

                if isinstance(item, tuple) and item[0] == "SET_PROPERTY":
                    props = item[1] if len(item) > 1 else {}
                    try:
                        if "voice" in props:
                            engine.setProperty("voice", props["voice"])
                        if "rate" in props:
                            engine.setProperty("rate", props["rate"])
                        if "volume" in props:
                            engine.setProperty("volume", props["volume"])
                    except Exception as exc:
                        print(f"[TTS ERROR] Property set failed: {type(exc).__name__}: {exc}")
                        self.gui_queue.put(("status", f"TTS property error: {exc}"))
                    finally:
                        self.tts_queue.task_done()
                    continue

                text = item
                if not text:
                    self.tts_queue.task_done()
                    continue

                print(f"[TTS] dequeued: {text}")
                self._tts_speaking = True
                self.gui_queue.put(("speaking_state", True))
                try:
                    print(f"[TTS] speaking: {text}")
                    engine.say(text)
                    print(f"[TTS] runAndWait starting")
                    engine.runAndWait()
                    print(f"[TTS] runAndWait returned")
                except Exception as exc:
                    print(f"[TTS ERROR] {type(exc).__name__}: {exc}")
                    self.gui_queue.put(("status", f"Voice output error: {exc}"))
                finally:
                    self.gui_queue.put(("speaking_state", False))
                    self._tts_speaking = False
                    self.tts_queue.task_done()
                    print(f"[TTS] completed")
        finally:
            print("[TTS] Worker loop exiting, cleaning up")
            if engine:
                try:
                    engine.stop()
                    print("[TTS] Engine stopped")
                except Exception as exc:
                    print(f"[TTS ERROR] Engine stop failed: {type(exc).__name__}: {exc}")
            if PYTHONCOM_AVAILABLE:
                try:
                    pythoncom.CoUninitialize()
                    print("[TTS] COM uninitialized")
                except Exception as exc:
                    print(f"[TTS ERROR] COM uninit failed: {type(exc).__name__}: {exc}")

    def _on_tts_toggled(self):
        """Handle the voice-response on/off checkbutton."""
        if not self.tts_enabled.get():
            while not self.tts_queue.empty():
                try:
                    self.tts_queue.get_nowait()
                    self.tts_queue.task_done()
                except queue.Empty:
                    break

    def _on_voice_selected(self, _event=None):
        """Apply the voice chosen in the combobox (queued to worker thread)."""
        index = self.voice_combo.current()
        if 0 <= index < len(self.voice_ids):
            self.tts_queue.put(("SET_PROPERTY", {"voice": self.voice_ids[index]}))

    def _on_rate_changed(self, value):
        """Apply the speech-rate slider value (queued to worker thread)."""
        rate = int(float(value))
        self.rate_value_label.configure(text=f"{rate} wpm")
        self.tts_queue.put(("SET_PROPERTY", {"rate": rate}))

    def _on_volume_changed(self, value):
        """Apply the volume slider value (queued to worker thread)."""
        volume = float(value)
        self.volume_value_label.configure(text=f"{int(round(volume * 100))}%")
        self.tts_queue.put(("SET_PROPERTY", {"volume": volume}))

    # ─── Actions from Assistant Core ──────────────────────────────────────
    def handle_action(self, action_data: dict):
        """Handle actions produced by the assistant core."""
        action = action_data.get("action")
        data = action_data.get("data") or {}

        if action == "open_url":
            site = data.get("site", "site")
            self._set_status(f"Opened {site} in your browser")
        elif action == "exit":
            self._set_status("Goodbye!")
            self.root.after(1200, self.on_closing)

    # ─── Shutdown ────────────────────────────────────────────────────────
    def on_closing(self):
        """Handle application closing."""
        self.listening = False
        self._stop_event.set()
        thread = self.listen_thread
        if thread and thread.is_alive():
            thread.join(timeout=1.5)

        self._tts_shutdown.set()
        self.tts_queue.put(None)
        if self.tts_worker_thread and self.tts_worker_thread.is_alive():
            self.tts_worker_thread.join(timeout=2.0)

        self.root.destroy()


def main():
    """Entry point for the application."""
    root = tk.Tk()
    app = VoiceAssistantApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()