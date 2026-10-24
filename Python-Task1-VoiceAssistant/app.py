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


# --------------------------------------------------------------------------
# Premium dark palette — electric violet / cyan on deep navy-black
# --------------------------------------------------------------------------
BG_MAIN      = "#0a0a14"   # window background
BG_PANEL     = "#101020"   # sidebar / header panels
BG_CARD      = "#171728"   # cards and conversation area
BG_INPUT     = "#1e1e32"   # input fields
BORDER       = "#2b2b48"   # hairline borders
TEXT_PRIMARY = "#eef2ff"   # primary text
TEXT_MUTED   = "#8b93b8"   # secondary text
VIOLET       = "#8b5cf6"   # primary accent
VIOLET_SOFT  = "#c4b5fd"   # user messages
CYAN         = "#22d3ee"   # secondary accent
CYAN_SOFT    = "#a5f3fc"   # assistant labels
SUCCESS      = "#34d399"
WARNING      = "#fbbf24"
DANGER       = "#f87171"


def _hex_lerp(color_a: str, color_b: str, t: float) -> str:
    """Linearly interpolate between two #rrggbb colors (0.0 -> a, 1.0 -> b)."""
    r = int(color_a[1:3], 16) + int((int(color_b[1:3], 16) - int(color_a[1:3], 16)) * t)
    g = int(color_a[3:5], 16) + int((int(color_b[3:5], 16) - int(color_a[3:5], 16)) * t)
    b = int(color_a[5:7], 16) + int((int(color_b[5:7], 16) - int(color_a[5:7], 16)) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


class VoiceAssistantApp:
    """Main Tkinter application for the voice assistant."""

    VIS_BAR_COUNT = 26   # visualizer bars
    VIS_WIDTH = 240      # visualizer canvas width
    VIS_HEIGHT = 46      # visualizer canvas height

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Voice Assistant — OIBSIP Task 1")
        self.root.geometry("1040x680")
        self.root.minsize(880, 560)
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

        # Text-to-speech engine
        self.tts_engine = None
        self.speaking = False
        self.tts_enabled = tk.BooleanVar(value=True)
        self.voice_names: list = []
        self.voice_ids: list = []

        # Thread communication: every GUI update flows through this queue
        self.gui_queue: "queue.Queue[tuple[str, object]]" = queue.Queue()

        # Visualizer state
        self.vis_phase = 0.0
        self.vis_heights = [4.0] * self.VIS_BAR_COUNT
        self.vis_bars: list = []
        self.vis_x: list = []

        # GUI setup
        self.setup_styles()
        self.create_widgets()
        self.initialize_speech_components()

        # Start queue processor + visualizer loop
        self._poll_gui_queue()
        self._draw_visualizer()

        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Welcome message
        self.add_message(
            "Assistant",
            "Hello! I'm your voice assistant. Click LISTEN and speak, "
            "or type a command below. Try 'help' to see what I can do.",
            "assistant",
        )
        self._set_status("Ready")

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------
    def setup_styles(self):
        """Configure ttk styles for the dark theme."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=BG_PANEL)
        style.configure("TLabel", background=BG_PANEL, foreground=TEXT_PRIMARY)
        style.configure("TScale", background=BG_PANEL, troughcolor=BORDER)
        style.configure(
            "TCombobox",
            fieldbackground=BG_INPUT,
            foreground=TEXT_PRIMARY,
            background=BG_INPUT,
            arrowcolor=TEXT_PRIMARY,
        )

    @staticmethod
    def _hover(button: tk.Button, base: str, hover: str):
        """Add a simple hover highlight to a flat tk.Button."""
        button.bind("<Enter>", lambda _e: button.configure(bg=hover))
        button.bind("<Leave>", lambda _e: button.configure(bg=base))

    def _card(self, parent, padding=12):
        """Create a dark card frame with a hairline border."""
        return tk.Frame(
            parent,
            bg=BG_CARD,
            highlightthickness=1,
            highlightbackground=BORDER,
            padx=padding,
            pady=padding,
        )

    def _section_title(self, parent, text):
        """Small uppercase section heading."""
        return tk.Label(
            parent,
            text=text.upper(),
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Segoe UI", 8, "bold"),
        )

    # ------------------------------------------------------------------
    # Widget layout
    # ------------------------------------------------------------------
    def create_widgets(self):
        """Create and layout all GUI components."""
        # ---- header ---------------------------------------------------
        header = tk.Frame(self.root, bg=BG_PANEL, height=86)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)

        title_wrap = tk.Frame(header, bg=BG_PANEL)
        title_wrap.pack(side=tk.LEFT, padx=22, pady=14)

        tk.Label(
            title_wrap,
            text="VOICE",
            bg=BG_PANEL,
            fg=VIOLET,
            font=("Segoe UI", 22, "bold"),
        ).pack(side=tk.LEFT)
        tk.Label(
            title_wrap,
            text="ASSISTANT",
            bg=BG_PANEL,
            fg=CYAN,
            font=("Segoe UI", 22, "bold"),
        ).pack(side=tk.LEFT)
        tk.Label(
            title_wrap,
            text="   OIBSIP · Task 1",
            bg=BG_PANEL,
            fg=TEXT_MUTED,
            font=("Segoe UI", 10),
        ).pack(side=tk.LEFT, pady=(10, 0))

        # Live status pill (top right of header)
        self.status_pill = tk.Label(
            header,
            text="● Ready",
            bg=BG_PANEL,
            fg=SUCCESS,
            font=("Segoe UI", 10, "bold"),
        )
        self.status_pill.pack(side=tk.RIGHT, padx=22, pady=14)

        # Audio visualizer (header, right of status)
        self.vis_canvas = tk.Canvas(
            header,
            width=self.VIS_WIDTH,
            height=self.VIS_HEIGHT,
            bg=BG_PANEL,
            highlightthickness=0,
        )
        self.vis_canvas.pack(side=tk.RIGHT, padx=(0, 18), pady=20)
        self._build_visualizer()

        # ---- body: conversation (left) + settings sidebar (right) ----
        body = tk.Frame(self.root, bg=BG_MAIN)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        left = tk.Frame(body, bg=BG_MAIN)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(18, 9), pady=(0, 14))

        sidebar = tk.Frame(body, bg=BG_MAIN, width=272)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(9, 18), pady=(0, 14))
        sidebar.pack_propagate(False)

        self._build_conversation(left)
        self._build_input_bar(left)
        self._build_sidebar(sidebar)

        # ---- bottom status bar ----------------------------------------
        status_bar = tk.Frame(self.root, bg=BG_PANEL, height=26)
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
        self.status_label.pack(side=tk.LEFT, padx=18)

        self.engine_label = tk.Label(
            status_bar,
            text="mic: —  ·  voice: —",
            bg=BG_PANEL,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
            anchor=tk.E,
        )
        self.engine_label.pack(side=tk.RIGHT, padx=18)

    def _build_visualizer(self):
        """Create the animated bars of the audio visualizer."""
        bar_w = 5
        gap = 4
        total = self.VIS_BAR_COUNT * bar_w + (self.VIS_BAR_COUNT - 1) * gap
        start_x = (self.VIS_WIDTH - total) // 2
        for i in range(self.VIS_BAR_COUNT):
            x = start_x + i * (bar_w + gap)
            self.vis_x.append(x)
            # gradient: violet (left) -> cyan (right)
            color = _hex_lerp(VIOLET, CYAN, i / max(self.VIS_BAR_COUNT - 1, 1))
            self.vis_bars.append(
                self.vis_canvas.create_rectangle(
                    x, self.VIS_HEIGHT - 4, x + bar_w, self.VIS_HEIGHT - 4,
                    fill=color, outline="",
                )
            )

    def _build_conversation(self, parent):
        """Conversation history area with chat-style message tags."""
        conv_card = self._card(parent, padding=0)
        conv_card.pack(fill=tk.BOTH, expand=True)

        self.conversation = scrolledtext.ScrolledText(
            conv_card,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            state="disabled",
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            selectbackground=VIOLET,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            padx=14,
            pady=10,
        )
        self.conversation.pack(fill=tk.BOTH, expand=True)

        # Chat-style tags: user messages right-aligned in violet,
        # assistant messages left-aligned in soft white.
        self.conversation.tag_configure(
            "user_name", foreground=VIOLET, justify="right",
            font=("Segoe UI", 8, "bold"), spacing3=2,
        )
        self.conversation.tag_configure(
            "user", foreground="#ddd6fe", justify="right",
            font=("Segoe UI", 10), spacing3=12,
        )
        self.conversation.tag_configure(
            "assistant_name", foreground=CYAN, justify="left",
            font=("Segoe UI", 8, "bold"), spacing3=2,
        )
        self.conversation.tag_configure(
            "assistant", foreground="#c8cee0", justify="left",
            font=("Segoe UI", 10), spacing3=12,
        )

    def _build_input_bar(self, parent):
        """Text input + send / listen / clear controls."""
        bar = tk.Frame(parent, bg=BG_MAIN)
        bar.pack(fill=tk.X, pady=(12, 0))

        self.text_entry = tk.Entry(
            bar,
            font=("Segoe UI", 11),
            bg=BG_INPUT,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        self.text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=7)
        self.text_entry.bind("<Return>", lambda _e: self.send_text_command())

        self.send_button = tk.Button(
            bar, text="SEND", command=self.send_text_command,
            bg=VIOLET, fg="white", activebackground="#7c3aed", activeforeground="white",
            font=("Segoe UI", 10, "bold"), relief="flat", padx=16,
        )
        self.send_button.pack(side=tk.LEFT, padx=(8, 0))
        self._hover(self.send_button, VIOLET, "#7c3aed")

        self.listen_button = tk.Button(
            bar, text="● LISTEN", command=self.toggle_listening,
            bg=VIOLET, fg="white", activebackground="#7c3aed", activeforeground="white",
            font=("Segoe UI", 10, "bold"), relief="flat", padx=16,
        )
        self.listen_button.pack(side=tk.LEFT, padx=(8, 0))
        self._hover(self.listen_button, VIOLET, "#7c3aed")

        self.clear_button = tk.Button(
            bar, text="CLEAR", command=self.clear_conversation,
            bg=BG_INPUT, fg=TEXT_MUTED, activebackground=BORDER, activeforeground=TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold"), relief="flat", padx=12,
        )
        self.clear_button.pack(side=tk.LEFT, padx=(8, 0))
        self._hover(self.clear_button, BG_INPUT, BORDER)

    def _build_sidebar(self, parent):
        """Right-hand settings sidebar: microphone, voice, quick commands."""
        # ---- microphone card ----
        mic_card = self._card(parent)
        mic_card.pack(fill=tk.X, pady=(0, 12))
        self._section_title(mic_card, "Microphone").pack(anchor=tk.W)

        self.mic_status_label = tk.Label(
            mic_card, text="Checking…", bg=BG_CARD, fg=TEXT_MUTED,
            font=("Segoe UI", 9), wraplength=230, justify=tk.LEFT,
        )
        self.mic_status_label.pack(anchor=tk.W, pady=(6, 8))

        self.retry_mic_button = tk.Button(
            mic_card, text="RETRY MICROPHONE", command=self._init_microphone,
            bg=BG_INPUT, fg=TEXT_MUTED, activebackground=BORDER, activeforeground=TEXT_PRIMARY,
            font=("Segoe UI", 8, "bold"), relief="flat",
        )
        self.retry_mic_button.pack(anchor=tk.W)
        self._hover(self.retry_mic_button, BG_INPUT, BORDER)

        # ---- voice output card ----
        voice_card = self._card(parent)
        voice_card.pack(fill=tk.X, pady=(0, 12))
        self._section_title(voice_card, "Voice Output").pack(anchor=tk.W)

        self.tts_status_label = tk.Label(
            voice_card, text="Checking…", bg=BG_CARD, fg=TEXT_MUTED,
            font=("Segoe UI", 9), wraplength=230, justify=tk.LEFT,
        )
        self.tts_status_label.pack(anchor=tk.W, pady=(6, 8))

        self.tts_check = tk.Checkbutton(
            voice_card, text="Enable voice responses",
            variable=self.tts_enabled, command=self._on_tts_toggled,
            bg=BG_CARD, fg=TEXT_PRIMARY, selectcolor=BG_INPUT,
            activebackground=BG_CARD, activeforeground=TEXT_PRIMARY,
            font=("Segoe UI", 9),
        )
        self.tts_check.pack(anchor=tk.W)

        tk.Label(
            voice_card, text="Voice", bg=BG_CARD, fg=TEXT_MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor=tk.W, pady=(10, 2))
        self.voice_combo = ttk.Combobox(
            voice_card, state="readonly", width=28, font=("Segoe UI", 9),
        )
        self.voice_combo.pack(anchor=tk.W, fill=tk.X)
        self.voice_combo.bind("<<ComboboxSelected>>", self._on_voice_selected)

        tk.Label(
            voice_card, text="Speech rate", bg=BG_CARD, fg=TEXT_MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor=tk.W, pady=(10, 2))
        self.rate_scale = ttk.Scale(
            voice_card, from_=100, to=300, value=180,
            command=self._on_rate_changed,
        )
        self.rate_scale.pack(anchor=tk.W, fill=tk.X)
        self.rate_value_label = tk.Label(
            voice_card, text="180 wpm", bg=BG_CARD, fg=TEXT_MUTED,
            font=("Segoe UI", 8),
        )
        self.rate_value_label.pack(anchor=tk.W)

        tk.Label(
            voice_card, text="Volume", bg=BG_CARD, fg=TEXT_MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor=tk.W, pady=(10, 2))
        self.volume_scale = ttk.Scale(
            voice_card, from_=0.0, to=1.0, value=0.9,
            command=self._on_volume_changed,
        )
        self.volume_scale.pack(anchor=tk.W, fill=tk.X)
        self.volume_value_label = tk.Label(
            voice_card, text="90%", bg=BG_CARD, fg=TEXT_MUTED,
            font=("Segoe UI", 8),
        )
        self.volume_value_label.pack(anchor=tk.W)

        # ---- quick commands card ----
        quick_card = self._card(parent)
        quick_card.pack(fill=tk.X)
        self._section_title(quick_card, "Quick Commands").pack(anchor=tk.W)

        quick_commands = [
            ("What time is it", "what time is it"),
            ("Today's date", "what's today's date"),
            ("Tell me a joke", "tell me a joke"),
            ("Open Google", "open google"),
            ("Open YouTube", "open youtube"),
            ("Help", "help"),
        ]
        for label, command in quick_commands:
            btn = tk.Button(
                quick_card, text=label, command=lambda c=command: self._quick_send(command),
                bg=BG_INPUT, fg=TEXT_PRIMARY, activebackground=VIOLET, activeforeground="white",
                font=("Segoe UI", 9), relief="flat", anchor=tk.W, padx=10, pady=2,
            )
            btn.pack(fill=tk.X, pady=(6, 0))
            self._hover(btn, BG_INPUT, VIOLET)

    # ------------------------------------------------------------------
    # Speech component initialization
    # ------------------------------------------------------------------
    def initialize_speech_components(self):
        """Initialize speech recognition and TTS engines."""
        self._init_microphone()
        self._init_tts()
        self._refresh_engine_label()

    def _init_microphone(self):
        """(Re)initialize the microphone; safe to call again on failure."""
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
                self.recognizer.energy_threshold = 300
                self.recognizer.dynamic_energy_threshold = True
            self.microphone = sr.Microphone()
            # Calibrate to ambient noise once per (re)init
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.mic_ok = True
            self._set_mic_status("Microphone ready. Click LISTEN and speak.")
        except Exception as exc:
            self.mic_ok = False
            self._set_mic_status(
                f"Microphone unavailable: {exc}. "
                "Install PyAudio (see README) or use typed commands."
            )
        finally:
            self._refresh_mic_ui()
            self._refresh_engine_label()

    def _init_tts(self):
        """Initialize the pyttsx3 text-to-speech engine."""
        self.tts_engine = None
        self.voice_names = []
        self.voice_ids = []
        if not TTS_AVAILABLE:
            self._set_tts_status(
                "pyttsx3 is not installed. The assistant will reply in text only. "
                "See requirements.txt."
            )
            self._refresh_engine_label()
            return
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty("rate", 180)
            self.tts_engine.setProperty("volume", 0.9)

            voices = self.tts_engine.getProperty("voices") or []
            self.voice_names = [v.name for v in voices]
            self.voice_ids = [v.id for v in voices]

            # Prefer a clearly female voice when one exists, else the first.
            preferred = None
            for i, voice in enumerate(voices):
                name = voice.name.lower()
                if "female" in name or "zira" in name or "samantha" in name:
                    preferred = i
                    break
            if preferred is None and voices:
                preferred = 0
            if preferred is not None:
                self.tts_engine.setProperty("voice", voices[preferred].id)

            if self.voice_names:
                self.voice_combo["values"] = self.voice_names
                self.voice_combo.current(preferred or 0)
            else:
                self.voice_combo["values"] = ["System default"]
                self.voice_combo.current(0)

            self._set_tts_status(
                f"Voice output ready — {len(self.voice_names)} voice(s) available."
            )
        except Exception as exc:
            self.tts_engine = None
            self._set_tts_status(f"Voice output error: {exc}. Text replies only.")
        finally:
            self._refresh_engine_label()

    def _refresh_mic_ui(self):
        """Sync the listen button and mic status dot with mic state."""
        if self.listening:
            return
        self.mic_status_label.configure(
            fg=SUCCESS if self.mic_ok else (TEXT_MUTED if not SPEECH_RECOGNITION_AVAILABLE else DANGER)
        )
        self.listen_button.configure(state=tk.NORMAL if self.mic_ok else tk.DISABLED)

    def _refresh_engine_label(self):
        """Update the bottom-right engine summary."""
        mic_text = "ok" if self.mic_ok else "off"
        voice_text = "ok" if self.tts_engine else "off"
        self.engine_label.configure(text=f"mic: {mic_text}  ·  voice: {voice_text}")

    # ------------------------------------------------------------------
    # Status + queue plumbing (all GUI updates happen on the main thread)
    # ------------------------------------------------------------------
    def _set_status(self, message: str):
        """Update the status bar and header pill (main thread only)."""
        self.status_label.configure(text=message)
        color = TEXT_MUTED
        lowered = message.lower()
        if "error" in lowered or "unavailable" in lowered or "unreachable" in lowered:
            color = DANGER
        elif "listening" in lowered or "speaking" in lowered:
            color = WARNING
        elif "ready" in lowered:
            color = SUCCESS
        self.status_pill.configure(text=f"● {message}", fg=color)

    def _set_mic_status(self, message: str):
        self.mic_status_label.configure(text=message)
        self._set_status(message)

    def _set_tts_status(self, message: str):
        self.tts_status_label.configure(text=message)

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
                    # Worker thread ended on its own — reset UI here.
                    self._reset_listening_ui()
                elif msg_type == "speaking_state":
                    if data:
                        self._set_status("Speaking…")
                    elif self.listening:
                        self._set_status("Listening… speak now")
                    else:
                        self._set_status("Ready")
                self.gui_queue.task_done()
        except queue.Empty:
            pass
        self.root.after(60, self._poll_gui_queue)

    # ------------------------------------------------------------------
    # Conversation display
    # ------------------------------------------------------------------
    def add_message(self, speaker: str, text: str, kind: str):
        """Append a chat-style message (main thread only)."""
        self.conversation.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M")
        self.conversation.insert(tk.END, f"{speaker}  ·  {timestamp}\n", f"{kind}_name")
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
        except Exception as exc:  # never let a bad command kill the GUI
            response = AssistantResponse(text=f"Something went wrong: {exc}")
        self.add_message("Assistant", response.text, "assistant")
        self.speak_text(response.text)
        if response.action:
            self.handle_action({
                "action": response.action,
                "data": response.action_data or {},
            })

    # ------------------------------------------------------------------
    # Listening (speech recognition)
    # ------------------------------------------------------------------
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
        if self.listening:
            return

        self.listening = True
        self._stop_event.clear()
        self.listen_button.configure(text="■ STOP", bg=DANGER, activebackground="#dc2626")
        self._set_status("Listening… speak now")
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
            text="● LISTEN", bg=VIOLET, activebackground="#7c3aed",
            state=tk.NORMAL if self.mic_ok else tk.DISABLED,
        )
        self._set_status("Ready")
        self._refresh_engine_label()

    def listen_loop(self):
        """Background thread: capture audio, recognize, queue results.

        Never touches Tkinter directly — everything goes through gui_queue.
        """
        while self.listening and not self._stop_event.is_set():
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(
                        source, timeout=2.0, phrase_time_limit=6.0,
                    )
            except sr.WaitTimeoutError:
                # Normal: no speech within the timeout window. Keep listening.
                continue
            except Exception as exc:
                self.gui_queue.put(("status", f"Microphone error: {exc}"))
                break

            try:
                text = self.recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                self.gui_queue.put(("status", "Didn't catch that — still listening"))
                continue
            except sr.RequestError as exc:
                # Speech-to-text service unreachable (offline / quota).
                self.gui_queue.put(("status", f"Speech service unreachable: {exc}"))
                continue

            if not text:
                continue

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

        # Loop ended without a user-initiated stop (error path) —
        # ask the main thread to restore the UI.
        if self.listening:
            self.gui_queue.put(("listening_state", False))

    # ------------------------------------------------------------------
    # Text-to-speech
    # ------------------------------------------------------------------
    def speak_text(self, text: str):
        """Speak text using the TTS engine (queued from any thread)."""
        if not self.tts_enabled.get() or not self.tts_engine or self.speaking:
            return
        threading.Thread(
            target=self._speak_worker, args=(text,), name="tts", daemon=True,
        ).start()

    def _speak_worker(self, text: str):
        """TTS worker thread: speak one response, then report back."""
        self.speaking = True
        self.gui_queue.put(("speaking_state", True))
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as exc:
            self.gui_queue.put(("status", f"Voice output error: {exc}"))
        finally:
            self.speaking = False
            self.gui_queue.put(("speaking_state", False))

    def _on_tts_toggled(self):
        """Handle the voice-response on/off checkbutton."""
        if not self.tts_enabled.get() and self.tts_engine:
            try:
                self.tts_engine.stop()
            except Exception:
                pass

    def _on_voice_selected(self, _event=None):
        """Apply the voice chosen in the combobox."""
        index = self.voice_combo.current()
        if 0 <= index < len(self.voice_ids) and self.tts_engine:
            try:
                self.tts_engine.setProperty("voice", self.voice_ids[index])
            except Exception:
                pass

    def _on_rate_changed(self, value):
        """Apply the speech-rate slider value."""
        rate = int(float(value))
        self.rate_value_label.configure(text=f"{rate} wpm")
        if self.tts_engine:
            try:
                self.tts_engine.setProperty("rate", rate)
            except Exception:
                pass

    def _on_volume_changed(self, value):
        """Apply the volume slider value."""
        volume = float(value)
        self.volume_value_label.configure(text=f"{int(round(volume * 100))}%")
        if self.tts_engine:
            try:
                self.tts_engine.setProperty("volume", volume)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Actions from the assistant core
    # ------------------------------------------------------------------
    def handle_action(self, action_data: dict):
        """Handle actions produced by the assistant core."""
        action = action_data.get("action")
        data = action_data.get("data") or {}

        if action == "open_url":
            # NOTE: assistant_core._handle_open already opened the allowlisted
            # URL (its unit tests assert that call). Opening it here too would
            # launch a second browser tab, so the GUI only reports success.
            site = data.get("site", "site")
            self._set_status(f"Opened {site} in your browser")
        elif action == "exit":
            self._set_status("Goodbye!")
            self.root.after(1200, self.on_closing)  # delay to show the message

    # ------------------------------------------------------------------
    # Visualizer animation
    # ------------------------------------------------------------------
    def _draw_visualizer(self):
        """Animate the visualizer bars; called on the main thread."""
        active = self.listening or self.speaking
        self.vis_phase += 0.30
        for i, bar in enumerate(self.vis_bars):
            if active:
                wave = abs(math.sin(self.vis_phase + i * 0.55))
                target = 5.0 + wave * 30.0 * (0.6 + 0.4 * random.random())
            else:
                target = 4.0
            # Smooth towards the target height for a fluid look.
            self.vis_heights[i] += (target - self.vis_heights[i]) * 0.35
            h = self.vis_heights[i]
            x = self.vis_x[i]
            self.vis_canvas.coords(
                bar, x, self.VIS_HEIGHT - h, x + 5, self.VIS_HEIGHT,
            )
        self.root.after(60, self._draw_visualizer)

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------
    def on_closing(self):
        """Handle application closing."""
        self.listening = False
        self._stop_event.set()
        thread = self.listen_thread
        if thread and thread.is_alive():
            thread.join(timeout=1.5)
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except Exception:
                pass
        self.root.destroy()


def main():
    """Entry point for the application."""
    root = tk.Tk()
    app = VoiceAssistantApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
