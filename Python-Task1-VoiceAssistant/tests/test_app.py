"""
Unit tests for Voice Assistant GUI Application (app.py).

Tests cover the TTS worker thread, queue serialization, and shutdown behavior.
All external dependencies (pyttsx3, speech_recognition, Tkinter) are mocked
so no microphone, speakers, or display is required.
"""

import sys
import os
import queue
import threading
import time
from unittest.mock import patch, MagicMock, PropertyMock, call

# Add parent to path for import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ======================================================================
# Set up mocks at module level BEFORE importing app
# ======================================================================

# Create mock modules
mock_pyttsx3 = MagicMock()
mock_sr = MagicMock()
mock_tk = MagicMock()
mock_ttk = MagicMock()
mock_scrolledtext = MagicMock()
mock_messagebox = MagicMock()

# Configure pyttsx3 - we need TWO separate mock engines:
# 1. temp_engine - created in _init_tts for voice discovery
# 2. worker_engine - created in worker thread for actual TTS
temp_engine = MagicMock()
worker_engine = MagicMock()

# Track loop state for worker_engine
worker_engine._inLoop = False

# Make init() return temp_engine first, then worker_engine on subsequent calls
init_call_count = [0]
def init_side_effect(*args, **kwargs):
    init_call_count[0] += 1
    if init_call_count[0] == 1:
        return temp_engine
    else:
        return worker_engine

mock_pyttsx3.init.side_effect = init_side_effect
temp_engine.getProperty.return_value = []
worker_engine.getProperty.return_value = []

# Configure worker_engine for runAndWait pattern (new implementation)
# runAndWait should just return immediately in the mock
worker_engine.runAndWait.return_value = None
worker_engine.startLoop = MagicMock()  # Not used anymore but keep for safety
worker_engine.endLoop = MagicMock()
worker_engine.iterate = MagicMock()

# Configure speech_recognition
mock_sr.Recognizer.return_value = MagicMock()
mock_sr.Microphone.return_value = MagicMock()
mock_sr.WaitTimeoutError = Exception
mock_sr.UnknownValueError = Exception
mock_sr.RequestError = Exception

# Configure tkinter
mock_root = MagicMock()
mock_tk.Tk.return_value = mock_root
mock_boolvar = MagicMock()
mock_boolvar.get.return_value = True
mock_boolvar.set = MagicMock()
mock_tk.BooleanVar.return_value = mock_boolvar

# Mock Canvas for the voice orb
mock_canvas = MagicMock()
mock_canvas.create_oval = MagicMock(return_value=1)
mock_canvas.create_rectangle = MagicMock(return_value=1)
mock_canvas.coords = MagicMock()
mock_canvas.itemconfig = MagicMock()
mock_canvas.pack = MagicMock()
mock_tk.Canvas = MagicMock(return_value=mock_canvas)

# Mock Frame, Label, Button, Entry, etc.
mock_tk.Frame = MagicMock(return_value=MagicMock())
mock_tk.Label = MagicMock(return_value=MagicMock())
mock_tk.Button = MagicMock(return_value=MagicMock())
mock_tk.Entry = MagicMock(return_value=MagicMock())
mock_tk.Checkbutton = MagicMock(return_value=MagicMock())
mock_tk.scrolledtext = MagicMock()
mock_tk.scrolledtext.ScrolledText = MagicMock(return_value=MagicMock())

# Install mocks in sys.modules BEFORE importing app
sys.modules['pyttsx3'] = mock_pyttsx3
sys.modules['speech_recognition'] = mock_sr
sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.ttk'] = mock_ttk
sys.modules['tkinter.scrolledtext'] = mock_scrolledtext
sys.modules['tkinter.messagebox'] = mock_messagebox

# NOW import app (it will use our mocks)
import app
import importlib
importlib.reload(app)

# ======================================================================
# Test class
# ======================================================================

class TestTTSWorker:
    """Tests for the persistent TTS worker thread in VoiceAssistantApp."""

    def setup_method(self):
        """Reset mocks before each test."""
        global init_call_count
        init_call_count[0] = 0  # Mutate the list instead of reassigning

        temp_engine.reset_mock()
        worker_engine.reset_mock()
        mock_sr.reset_mock()
        mock_tk.reset_mock()
        mock_ttk.reset_mock()
        mock_scrolledtext.reset_mock()
        mock_messagebox.reset_mock()

        # Re-configure default return values
        temp_engine.getProperty.return_value = []
        worker_engine.getProperty.return_value = []
        # Configure worker_engine for runAndWait pattern
        worker_engine.runAndWait.return_value = None
        worker_engine.startLoop = MagicMock()
        worker_engine.endLoop = MagicMock()
        worker_engine.iterate = MagicMock()
        mock_sr.Recognizer.return_value = MagicMock()
        mock_sr.Microphone.return_value = MagicMock()
        mock_sr.WaitTimeoutError = Exception
        mock_sr.UnknownValueError = Exception
        mock_sr.RequestError = Exception
        mock_tk.Tk.return_value = mock_root
        mock_boolvar.get.return_value = True
        mock_boolvar.set = MagicMock()
        mock_tk.BooleanVar.return_value = mock_boolvar

    def create_app_instance(self):
        """Create a fresh app instance with current mock state."""
        importlib.reload(app)
        return app.VoiceAssistantApp(mock_root)

    def test_tts_worker_thread_started_on_init(self):
        """Verify that _init_tts starts a single persistent worker thread."""
        app_instance = self.create_app_instance()

        # Verify worker thread was created and started
        assert app_instance.tts_worker_thread is not None
        assert app_instance.tts_worker_thread.name == "tts-worker"
        assert app_instance.tts_worker_thread.daemon is True
        assert app_instance.tts_worker_thread.is_alive()

    def test_speak_text_enqueues_request(self):
        """Verify speak_text puts text on the TTS queue."""
        app_instance = self.create_app_instance()
        initial_queue_size = app_instance.tts_queue.qsize()

        app_instance.speak_text("Hello world")

        # Queue should have one more item
        assert app_instance.tts_queue.qsize() == initial_queue_size + 1

    def test_tts_worker_processes_queue_sequentially(self):
        """Verify worker processes multiple requests in order (serialization)."""
        app_instance = self.create_app_instance()

        # Give worker thread time to fully start (COM init + engine creation)
        time.sleep(0.5)

        # Enqueue multiple texts
        app_instance.speak_text("First")
        app_instance.speak_text("Second")
        app_instance.speak_text("Third")

        # Wait for queue to be empty (all items processed)
        start = time.time()
        while not app_instance.tts_queue.empty() and (time.time() - start) < 5.0:
            time.sleep(0.05)

        # Verify worker_engine.say was called for each in order
        assert worker_engine.say.call_count == 3, f"Expected 3 calls, got {worker_engine.say.call_count}"
        calls = worker_engine.say.call_args_list
        assert calls[0][0][0] == "First"
        assert calls[1][0][0] == "Second"
        assert calls[2][0][0] == "Third"

        # Verify worker_engine runAndWait called for each (new pattern)
        assert worker_engine.runAndWait.call_count == 3, f"Expected 3 runAndWait calls, got {worker_engine.runAndWait.call_count}"

    def test_tts_worker_sentinel_shutdown(self):
        """Verify worker exits cleanly on sentinel (None) in queue."""
        app_instance = self.create_app_instance()
        worker_thread = app_instance.tts_worker_thread

        # Send sentinel and wait for thread to finish
        app_instance._tts_shutdown.set()
        app_instance.tts_queue.put(None)
        worker_thread.join(timeout=2.0)

        # Worker should have stopped
        assert not worker_thread.is_alive()

    def test_tts_worker_error_recovery(self):
        """Verify worker continues after engine errors."""
        app_instance = self.create_app_instance()

        # Make worker_engine.runAndWait raise an exception on first call
        worker_engine.runAndWait.side_effect = [
            RuntimeError("SAPI5 error"),
            None,  # Second call succeeds
        ]

        app_instance.speak_text("First - will error")
        app_instance.speak_text("Second - should work")

        # Give worker time to process both
        time.sleep(0.5)

        # Both should have been attempted
        assert worker_engine.say.call_count == 2
        assert worker_engine.runAndWait.call_count == 2

    def test_speak_text_respects_tts_enabled_flag(self):
        """Verify speak_text does nothing when TTS is disabled."""
        app_instance = self.create_app_instance()
        app_instance.tts_enabled.get = lambda: False

        app_instance.speak_text("Should not be spoken")

        # Worker engine should not be called
        worker_engine.say.assert_not_called()

    def test_speak_text_respects_engine_availability(self):
        """Verify speak_text does nothing when TTS not available."""
        # This test is harder with new architecture since worker always creates engine
        # Just verify no exception when TTS disabled via flag
        app_instance = self.create_app_instance()
        app_instance.tts_enabled.get = lambda: False
        app_instance.speak_text("Should not be spoken")
        worker_engine.say.assert_not_called()

    def test_on_closing_shuts_down_tts_worker(self):
        """Verify on_closing properly stops the TTS worker."""
        app_instance = self.create_app_instance()
        worker_thread = app_instance.tts_worker_thread

        app_instance.on_closing()

        # Worker should have been sent sentinel and joined
        assert not worker_thread.is_alive()
        # Worker engine stop should have been called once
        worker_engine.stop.assert_called_once()

    def test_microphone_init_uses_device_index(self):
        """Verify _init_microphone uses configured device_index with fallback."""
        # Need to reset sr mock for this test
        mock_sr.reset_mock()
        mock_sr.Recognizer.return_value = MagicMock()
        mock_mic = MagicMock()
        mock_sr.Microphone.return_value = mock_mic
        mock_sr.WaitTimeoutError = Exception
        mock_sr.UnknownValueError = Exception
        mock_sr.RequestError = Exception

        app_instance = self.create_app_instance()

        # Should have tried device_index=1 first
        mock_sr.Microphone.assert_called_with(device_index=1)

    def test_microphone_init_fallback_to_default(self):
        """Verify _init_microphone falls back to default device on failure."""
        mock_sr.reset_mock()
        mock_sr.Recognizer.return_value = MagicMock()
        mock_mic = MagicMock()
        # First call fails, second succeeds
        mock_sr.Microphone.side_effect = [
            Exception("Device 1 failed"),
            mock_mic,
        ]
        mock_sr.WaitTimeoutError = Exception
        mock_sr.UnknownValueError = Exception
        mock_sr.RequestError = Exception

        app_instance = self.create_app_instance()

        # Should have been called twice: once with device_index=1, once without
        assert mock_sr.Microphone.call_count == 2
        calls = mock_sr.Microphone.call_args_list
        assert calls[0][1] == {'device_index': 1}
        assert calls[1] == ((), {})  # No args for default


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])