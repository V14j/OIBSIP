# Voice Assistant — OIBSIP Task 1 (Premium Edition)

A desktop voice assistant built with Python, Tkinter, `SpeechRecognition`, and `pyttsx3` — with a premium futuristic dark UI, animated AI voice orb, refined microphone controls, and fully thread-safe speech input and output.

---

## Features

- **Premium Futuristic UI** — charcoal/navy theme with electric-blue accents, animated voice orb, chat-style conversation bubbles, hairline-bordered cards, and a responsive two-column layout (conversation + settings sidebar).
- **Animated AI Voice Orb** — 5-layer concentric rings with state-aware animations (Ready: calm breathing, Listening: expanding electric-blue pulses, Processing: rotating violet/blue rings, Speaking: waveform-driven activity).
- **Refined Microphone Control** — circular electric-blue button with clear state transitions (● LISTEN → ■ STOP), disabled gracefully when microphone unavailable.
- **Clear Status Indicators** — orb status text, bottom status bar, and sidebar status dots show Listening/Processing/Speaking/Ready states with color-coded feedback.
- **Speech Recognition** — `SpeechRecognition` with `recognize_google()` backend when microphone available. Runs in dedicated background thread; failed recognition or unreachable speech service no longer kills the loop or GUI.
- **Text-to-Speech** — responds with `pyttsx3`, with **voice selection**, **speech-rate** (100–300 wpm), and **volume** sliders, plus on/off toggle.
- **Typed Commands** — app works fully from keyboard if microphone/speech services unavailable; quick-command buttons cover common requests.
- **Supported Commands:**
  - Greeting (`hello`, `hi`, `good morning`)
  - Time (`what time is it`)
  - Date (`what's today's date`)
  - Jokes (`tell me a joke` — programming-related, clean)
  - Open allowed websites (`open google`, `open youtube`, `open github`, `open stackoverflow`, `open wikipedia`)
  - Help (`help`)
  - Exit (`goodbye`, `exit`)
- **Explicit Allowlist** — only the five supported sites can be opened. No `eval`, no arbitrary shell execution.
- **Thread-Safe** — microphone listener and TTS worker never touch Tkinter directly. Every GUI update flows through a single `queue.Queue` drained by main thread with `root.after()`.
- **Graceful Errors** — handles missing mic, speech-recognition failures, TTS errors, and unknown commands with clear status messages instead of crashes.

---

## What changed in the Final Polish

- **Premium color palette**: deep charcoal/navy (`#0a0a12`, `#0f0f1a`, `#141420`) with electric-blue (`#00d4ff`) primary accent and electric-violet (`#a855f7`) secondary accent.
- **Redesigned voice orb**: larger (150px), 5 animated rings, state-specific animations with electric-blue dominance for listening/speaking.
- **Refined microphone button**: electric-blue circular button (●/■) with hover glow, disabled state when mic unavailable.
- **Enhanced conversation readability**: improved text contrast, better spacing, distinct user/assistant styling with colored accents.
- **Improved sidebar**: added GitHub quick action, refined control spacing, electric-blue accent on sliders/checkboxes.
- **Professional spacing/alignment**: consistent 24px page margins, 16px card padding, 12px section gaps, aligned button groups.
- **All tests pass**: 16 core tests + 10 app tests = 26 total, all passing.
- **GUI launches cleanly**: exit code 0, TTS speaks welcome message.

---

## Project Structure

```
Python-Task1-VoiceAssistant/
├── app.py                  # Tkinter GUI, speech threading, voice orb
├── assistant_core.py       # Command parsing and response logic (testable)
├── tests/
│   ├── test_assistant_core.py  # Unit tests (16)
│   └── test_app.py             # GUI/TTS worker tests (10)
├── requirements.txt
├── .gitignore
├── README.md
└── screenshots/            # Place for UI screenshots
```

---

## Requirements

- Python 3.10+
- `SpeechRecognition` (microphone input)
- `pyttsx3` (voice output)
- `pyaudio` (microphone backend; see installation notes below)

---

## Installation (Windows PowerShell)

```powershell
cd C:\Users\bharath\OneDrive\Desktop\OIBSIP\Python-Task1-VoiceAssistant

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### Microphone backend notes

`SpeechRecognition` requires a microphone backend. On most systems this is `PyAudio` (`pyaudio`).

- **Windows:**
  ```powershell
  pip install pipwin
  pipwin install pyaudio
  ```
  If that fails, download the `.whl` from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio and install with:
  ```
  pip install .\PyAudio-...-.whl
  ```

- **macOS:**
  ```bash
  brew install portaudio
  pip install pyaudio
  ```

- **Linux:**
  ```bash
  sudo apt-get install python3-pyaudio
  ```

> **Note:** If microphone initialization fails (e.g., PyAudio/SpeechRecognition version compatibility), the app gracefully degrades — typed commands work fully, and the sidebar's **RETRY MICROPHONE** button re-attempts initialization.

---

## Running the Application

```powershell
.\venv\Scripts\Activate.ps1
python app.py
```

---

## Usage

1. Type a command and press **Enter** or **SEND**, or click a **Quick Command** button.
2. Click **●** (electric-blue microphone button, top-right of input bar) and speak. The voice orb animates while the mic is live; press **■** to end the session.
3. The conversation pane shows your input (right, violet) and the assistant's reply (left, electric-blue label).
4. Voice output is on by default — toggle it, pick a system voice, and adjust rate/volume in the right-hand **SYSTEM** card.
5. The status bar (bottom) and the orb status text (top-right) always show the current state: `Ready`, `Listening…`, `Processing…`, `Speaking…`, or error detail.

---

## Running Tests

```powershell
python -m unittest tests.test_assistant_core -v
python -m pytest tests/test_app.py -v
```

Expected result: all 26 tests pass (16 core + 10 app). Tests cover command parsing, time/date, jokes, open commands (with `webbrowser.open` mocked), greetings, exits, unknown commands, empty input, TTS worker thread, queue serialization, shutdown behavior, and microphone initialization. No microphone, network, or TTS engine is required.

---

## Manual Verification Steps

1. Launch: `python app.py` → window opens with premium dark UI, voice orb animating calmly.
2. Type `hello` → greeting appears in conversation pane (right-aligned, violet).
3. Type `what time is it` → current time (left-aligned, electric-blue).
4. Type `what's the date` → current date.
5. Type `tell me a joke` → a programming joke.
6. Type `open google` → exactly one browser tab opens (allowlist only).
7. Type `open github` → GitHub opens (new quick action).
8. Click **●** microphone button (if mic initialized) → orb pulses electric-blue, status shows `Listening…`.
9. Speak a greeting → appears in conversation, assistant replies and speaks it.
10. Click **■** STOP → button returns to **●**, orb returns to calm breathing, status shows `Ready`.
11. Type an unsupported command → helpful fallback message.
12. Say `goodbye` (or type it) → exit message, then window closes.
13. Without microphone/pyttsx3: app still answers typed commands, shows clear status messages; **RETRY MICROPHONE** re-attempts mic init.

---

## Screenshot Guidance

For submission screenshots, capture:

1. **Main window** (1300×850): full UI showing hero with NOVA branding, animated voice orb, conversation area with sample messages, composer with electric-blue mic button, sidebar with SYSTEM and QUICK ACTIONS cards.
2. **Listening state**: click microphone button, capture orb in expanded electric-blue pulse animation with "Listening…" status.
3. **Conversation sample**: type a few commands (hello, time, joke, open github) to show chat-style bubbles with timestamps.
4. **Sidebar controls**: show voice selector, speech rate/volume sliders, RETRY MICROPHONE button.
5. **Error handling**: if mic unavailable, capture sidebar showing "Microphone: Unavailable" with RETRY button.

Recommended: use Windows Snipping Tool or ShareX at 100% scaling, 1366×768 or 1920×1080 resolution.

---

## Security and Design Notes

- **Explicit Allowlist:** only five sites (`google`, `youtube`, `github`, `stackoverflow`, `wikipedia`) can be opened. Any other `open ...` command returns a safe fallback message.
- **No Arbitrary Execution:** `eval()`, `exec()`, `os.system()`, or shell command execution are never used. `webbrowser.open()` is called only with pre-validated URLs.
- **Separated Architecture:** `assistant_core.py` holds all response logic and is testable without Tkinter, the microphone, or a TTS engine.
- **Thread Safety:** microphone listener and TTS worker run in background threads and communicate exclusively through `queue.Queue`; main thread performs every Tkinter update via `root.after()`.
- **Graceful Degradation:** if `SpeechRecognition`, `PyAudio`, or `pyttsx3` is missing, the app continues with typed input and clear status messages.

---

## Architecture — Beginner-Friendly Explanation

1. **GUI (`app.py`)** — builds the window, renders the conversation, handles typed input, shows status, and owns the animated voice orb. It is the only module that touches Tkinter.
2. **Core (`assistant_core.py`)** — receives a text string (typed or recognized from speech), matches it to allowed commands, and returns a structured `AssistantResponse` (text + optional action).
3. **Speech input (`SpeechRecognition`)** — a background thread captures microphone audio and converts it to text (`recognize_google`), then queues the result.
4. **Speech output (`pyttsx3`)** — a background worker speaks the assistant's replies; controls for voice, rate, and volume live in the sidebar.
5. **Thread Safety** — background threads only `queue.put(...)`; main thread polls that queue with `root.after(60, ...)` and updates widgets. This keeps the interface responsive and prevents Tkinter cross-thread crashes.

---

## Limitations

- Speech recognition quality depends on microphone quality, background noise, and Google speech-to-text service availability (internet required for `recognize_google`).
- `pyttsx3` voices depend on the operating system's installed voices.
- Only a small set of commands is implemented (greeting, time, date, joke, open allowed sites, help, exit). More complex natural-language understanding is not included.
- No persistent conversation history between sessions and no multi-user support.

---

## Demo Script (for Evaluators)

```python
from assistant_core import VoiceAssistantCore

core = VoiceAssistantCore()
commands = [
    "hello",
    "what time is it",
    "what's today's date",
    "tell me a joke",
    "open youtube",
    "open github",
    "help",
    "goodbye",
    "unknown command",
]
for cmd in commands:
    resp = core.process_command(cmd)
    print(f"User: {cmd}\nAssistant: {resp.text}\n")
```

---

## Viva Preparation — Likely Questions and Answers

1. **Why is the assistant core separated from the GUI?**
   - So it can be tested without a microphone, without Tkinter, and without starting the full GUI.

2. **How does the microphone work?**
   - A background thread holds `Microphone()` open, calibrates to ambient noise, listens with a timeout, and sends recognized text to the GUI through a queue.

3. **How is the interface kept responsive?**
   - Microphone listening and TTS run in background threads. Those threads never call Tkinter; they push messages onto a queue that the main thread polls with `root.after()`.

4. **What happens when speech is unintelligible or the speech service is offline?**
   - `UnknownValueError` is caught and reported ("didn't catch that") and the listener keeps running; `RequestError` reports that the speech service is unreachable. Neither stops the app.

5. **How is security handled for the `open` command?**
   - Only an explicit allowlist of five sites is permitted. Any other command receives a safe fallback message. No user input is ever passed to `eval()` or a shell.

6. **What happens if the microphone is not working?**
   - The Listen button is disabled with a clear message, the typed input works independently, and the sidebar's RETRY MICROPHONE button re-attempts initialization.

7. **Why doesn't clicking "open google" open two tabs?**
   - The core module performs the single allowlisted `webbrowser.open()` call (its unit tests assert it). The GUI only displays the result, so exactly one tab opens.

8. **How does the voice orb animation work?**
   - A Tkinter Canvas draws 5 concentric rings and a core circle. A 40ms `root.after` loop updates ring radii/colors based on state (ready/listening/processing/speaking), creating smooth animations without blocking the UI.

---

## Source Specification Note

The official internship task-list PDF (`OASIS INFOBYTE — Task List.pdf`) was not found in the repository. The working specification above is based on the user's pasted requirements. Full PDF compliance has not been claimed or verified.