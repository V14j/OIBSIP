# Voice Assistant — OIBSIP Task 1 (Premium Edition)

A desktop voice assistant built with Python, Tkinter, `SpeechRecognition`, and `pyttsx3` — with a modern dark UI, animated audio visualizer, voice controls, and fully thread-safe speech input and output.

---

## Features

- **Premium dark UI** — deep-navy theme with electric-violet and cyan accents, chat-style conversation bubbles, hairline-bordered cards, and a responsive two-column layout (conversation + settings sidebar).
- **Animated audio visualizer** — 26 gradient bars (violet → cyan) in the header that animate while listening or speaking.
- **Speech Recognition** — `SpeechRecognition` with the `recognize_google()` backend when a microphone is available. Runs in a dedicated background thread; a failed recognition or unreachable speech service no longer kills the loop or the GUI.
- **Text-to-Speech** — responds with `pyttsx3`, with **voice selection**, **speech-rate** (100–300 wpm), and **volume** sliders, plus an on/off toggle.
- **Typed Commands** — the app works fully from the keyboard if the microphone or speech services are unavailable; quick-command buttons cover the most common requests.
- **Supported Commands:**
  - Greeting (`hello`, `hi`, `good morning`)
  - Time (`what time is it`)
  - Date (`what's today's date`)
  - Jokes (`tell me a joke` — programming-related, clean)
  - Open allowed websites (`open google`, `open youtube`, `open github`, `open stackoverflow`, `open wikipedia`)
  - Help (`help`)
  - Exit (`goodbye`, `exit`)
- **Explicit Allowlist** — only the five supported sites can be opened. No `eval`, no arbitrary shell execution.
- **Thread-Safe** — the microphone listener and the TTS worker never touch Tkinter directly. Every GUI update flows through a single `queue.Queue` drained by the main thread with `root.after()`.
- **Graceful Errors** — handles missing mic, speech-recognition failures, TTS errors, and unknown commands with clear status messages instead of crashes.

---

## What changed in the Premium upgrade

- **Fixed GUI-thread crashes:** the old microphone loop called `stop_listening()` (a Tkinter update) from the worker thread and let `WaitTimeoutError` escape, which ended listening silently and could crash the GUI. The listener now signals via the queue, swallows wait timeouts, and keeps listening until you press STOP.
- **Fixed double browser launch:** `assistant_core._handle_open` already opens the allowlisted URL (its unit tests assert that call), so the GUI now only reports success instead of opening a second tab.
- **Fixed lost replies:** `UnknownValueError` (unintelligible speech) and `RequestError` (speech service offline) previously printed nothing; they now report clearly and the loop continues.
- **Fixed mic lockout:** a failed `Microphone()` init left the Listen button disabled permanently; a RETRY MICROPHONE button now re-attempts init without restarting the app.
- **UI redesign:** header with title/status/visualizer, chat-style conversation history, dark input bar, and a settings sidebar (microphone status, voice output controls, quick commands).
- **New voice controls:** choose among installed system voices, adjust speech rate and volume, or mute voice output while keeping text replies.

---

## Project Structure

```
Python-Task1-VoiceAssistant/
├── app.py                  # Tkinter GUI, speech threading, visualizer
├── assistant_core.py       # Command parsing and response logic (testable)
├── tests/
│   └── test_assistant_core.py  # Unit tests (16)
├── requirements.txt
├── .gitignore
├── README.md
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

---

## Running the Application

```powershell
.\venv\Scripts\Activate.ps1
python app.py
```

---

## Usage

1. Type a command and press **Enter** or **SEND**, or click a **Quick Command** button.
2. Click **● LISTEN** (top-right of the input bar) and speak. The header visualizer animates while the mic is live; press **■ STOP** to end the session.
3. The conversation pane shows your input (right, violet) and the assistant's reply (left, cyan label).
4. Voice output is on by default — toggle it, pick a system voice, and adjust rate/volume in the right-hand **Voice Output** card.
5. The status bar (bottom) and the status pill (top-right header) always show the current state: `Ready`, `Listening…`, `Speaking…`, or the error detail.

---

## Running Tests

```powershell
python -m unittest tests.test_assistant_core -v
```

Expected result: all 16 tests pass. Tests cover command parsing, time/date, jokes, open commands (with `webbrowser.open` mocked), greetings, exits, unknown commands, and empty input. No microphone, network, or TTS engine is required.

---

## Manual Verification Steps

1. Launch: `python app.py`
2. Type `hello` → greeting appears in the conversation pane.
3. Type `what time is it` → current time.
4. Type `what's the date` → current date.
5. Type `tell me a joke` → a programming joke.
6. Click **● LISTEN** (if the mic initialized) → speak a greeting → it appears in the conversation and the assistant replies (and speaks it).
7. Click **■ STOP** → the button returns to **● LISTEN** and status shows `Ready`.
8. Type `open google` → exactly one browser tab opens (allowlist only).
9. Type an unsupported command → helpful fallback message.
10. Say `goodbye` (or type it) → exit message, then the window closes.
11. Without a microphone or `pyttsx3` installed, the app still answers typed commands and shows clear status messages; the sidebar's **RETRY MICROPHONE** re-attempts mic init.

---

## Security and Design Notes

- **Explicit Allowlist:** only five sites (`google`, `youtube`, `github`, `stackoverflow`, `wikipedia`) can be opened. Any other `open ...` command returns a safe fallback message.
- **No Arbitrary Execution:** `eval()`, `exec()`, `os.system()`, or shell command execution are never used. `webbrowser.open()` is called only with pre-validated URLs.
- **Separated Architecture:** `assistant_core.py` holds all response logic and is testable without Tkinter, the microphone, or a TTS engine.
- **Thread Safety:** the microphone listener and TTS worker run in background threads and communicate exclusively through `queue.Queue`; the main thread performs every Tkinter update via `root.after()`.
- **Graceful Degradation:** if `SpeechRecognition`, `PyAudio`, or `pyttsx3` is missing, the app continues with typed input and clear status messages.

---

## Architecture — Beginner-Friendly Explanation

1. **GUI (`app.py`)** — builds the window, renders the conversation, handles typed input, shows status, and owns the visualizer. It is the only module that touches Tkinter.
2. **Core (`assistant_core.py`)** — receives a text string (typed or recognized from speech), matches it to allowed commands, and returns a structured `AssistantResponse` (text + optional action).
3. **Speech input (`SpeechRecognition`)** — a background thread captures microphone audio and converts it to text (`recognize_google`), then queues the result.
4. **Speech output (`pyttsx3`)** — a background worker speaks the assistant's replies; controls for voice, rate, and volume live in the sidebar.
5. **Thread Safety** — background threads only `queue.put(...)`; the main thread polls that queue with `root.after(60, ...)` and updates the widgets. This keeps the interface responsive and prevents Tkinter cross-thread crashes.

---

## Limitations

- Speech recognition quality depends on microphone quality, background noise, and the Google speech-to-text service availability (an internet connection is required for `recognize_google`).
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

---

## Source Specification Note

The official internship task-list PDF (`OASIS INFOBYTE — Task List.pdf`) was not found in the repository. The working specification above is based on the user's pasted requirements. Full PDF compliance has not been claimed or verified.
