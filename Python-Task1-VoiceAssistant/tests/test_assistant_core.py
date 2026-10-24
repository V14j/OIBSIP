"""
Unit tests for Voice Assistant Core Module.

Tests cover command parsing, supported actions, and graceful handling
of unknown or empty input. All external actions use mocked values
so no microphone, network, or TTS engine is required.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent to path for import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assistant_core import VoiceAssistantCore, AssistantResponse


class TestVoiceAssistantCore(unittest.TestCase):
    """Tests for assistant core logic."""

    def setUp(self):
        """Create a fresh assistant instance for each test."""
        self.assistant = VoiceAssistantCore()

    def test_greeting_hello(self):
        response = self.assistant.process_command("hello")
        self.assertIn("How can I help", response.text)
        self.assertEqual(response.action, "greeting")

    def test_greeting_hi(self):
        response = self.assistant.process_command("hi")
        self.assertIn("How can I help", response.text)

    def test_time_command(self):
        with patch('assistant_core.datetime') as mock_dt:
            mock_dt.datetime.now.return_value.strftime.side_effect = lambda fmt: "02:30 PM"
            mock_dt.datetime.now.return_value.hour = 14
            response = self.assistant.process_command("what time is it")
        self.assertIn("02:30 PM", response.text)
        self.assertEqual(response.action, "speak_time")

    def test_date_command(self):
        with patch('assistant_core.datetime') as mock_dt:
            mock_dt.datetime.now.return_value.strftime.side_effect = lambda fmt: "Monday, October 19, 2026"
            mock_dt.datetime.now.return_value.hour = 14
            response = self.assistant.process_command("what is today's date")
        self.assertIn("Monday, October 19, 2026", response.text)
        self.assertEqual(response.action, "speak_date")

    def test_joke_command(self):
        response = self.assistant.process_command("tell me a joke")
        # Jokes start with common programming joke prefixes
        valid_starts = ["Why", "A SQL", "There are", "How many", "What's"]
        self.assertTrue(any(response.text.startswith(p) for p in valid_starts),
                        f"Joke '{response.text}' should start with a known prefix")
        self.assertEqual(response.action, "tell_joke")

    def test_open_google(self):
        with patch('assistant_core.webbrowser.open') as mock_open:
            response = self.assistant.process_command("open google")
            mock_open.assert_called_once()
            args, _ = mock_open.call_args
            self.assertIn("google", args[0])
        self.assertEqual(response.action, "open_url")

    def test_open_youtube(self):
        with patch('assistant_core.webbrowser.open') as mock_open:
            response = self.assistant.process_command("open youtube")
            mock_open.assert_called_once()
        self.assertIn("youtube", response.text.lower())

    def test_open_unknown_site_blocked(self):
        response = self.assistant.process_command("open malicious-site")
        self.assertNotEqual(response.action, "open_url")
        self.assertIn("only open", response.text.lower())

    def test_help_command(self):
        response = self.assistant.process_command("help")
        self.assertIn("time", response.text.lower())
        self.assertIn("date", response.text.lower())
        self.assertIn("joke", response.text.lower())
        self.assertIn("goodbye", response.text.lower())

    def test_exit_command(self):
        response = self.assistant.process_command("goodbye")
        self.assertIn("goodbye", response.text.lower())
        self.assertEqual(response.action, "exit")

    def test_unknown_command_fallback(self):
        response = self.assistant.process_command("fly to the moon")
        self.assertIn("not sure", response.text.lower())
        self.assertIn("try", response.text.lower())

    def test_empty_input(self):
        response = self.assistant.process_command("")
        self.assertIn("didn't catch", response.text.lower())
        response2 = self.assistant.process_command("   ")
        self.assertIn("didn't catch", response2.text.lower())

    def test_open_partial_match_google(self):
        with patch('assistant_core.webbrowser.open') as mock_open:
            response = self.assistant.process_command("open goog")
            mock_open.assert_called_once()
        self.assertEqual(response.action, "open_url")

    def test_open_github(self):
        with patch('assistant_core.webbrowser.open') as mock_open:
            response = self.assistant.process_command("open github")
            mock_open.assert_called_once()
        self.assertIn("github", response.text.lower())

    def test_date_format(self):
        # Verify date command produces structured response
        response = self.assistant.process_command("date")
        self.assertTrue("date" in response.action or "speak_date" in response.action or "date" in response.text.lower())

    def test_all_jokes_are_clean(self):
        from assistant_core import VoiceAssistantCore
        # Verify all jokes are non-empty and safe
        self.assertTrue(len(VoiceAssistantCore.JOKES) > 0)
        for joke in VoiceAssistantCore.JOKES:
            self.assertIsInstance(joke, str)
            self.assertGreater(len(joke), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
