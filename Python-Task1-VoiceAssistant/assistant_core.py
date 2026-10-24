"""
Voice Assistant Core Module

Handles command parsing, response generation, and supported actions.
Separated from GUI for testability and clarity.
"""

import datetime
import webbrowser
import random
from typing import Optional, Tuple, Dict, Callable
from dataclasses import dataclass


@dataclass
class AssistantResponse:
    """Structured response from the assistant."""
    text: str
    action: Optional[str] = None  # e.g., "open_url", "speak_time"
    action_data: Optional[Dict] = None


class VoiceAssistantCore:
    """Core logic for the voice assistant - handles commands and generates responses."""

    # Explicitly allowed websites - security: only these can be opened
    ALLOWED_SITES: Dict[str, str] = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "github": "https://github.com",
        "stackoverflow": "https://stackoverflow.com",
        "wikipedia": "https://www.wikipedia.org",
    }

    # Programming jokes (clean, student-friendly)
    JOKES = [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "Why did the programmer quit his job? Because he didn't get arrays!",
        "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
        "There are 10 types of people in the world: those who understand binary and those who don't.",
        "Why do Python programmers wear glasses? Because they can't C#!",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
        "Why was the JavaScript developer sad? Because he didn't Node how to Express himself!",
        "What's a programmer's favorite hangout place? Foo Bar!",
    ]

    def __init__(self):
        """Initialize the assistant core."""
        self.command_handlers: Dict[str, Callable[[str], AssistantResponse]] = {
            "help": self._handle_help,
            "time": self._handle_time,
            "date": self._handle_date,
            "joke": self._handle_joke,
            "open": self._handle_open,
            "greeting": self._handle_greeting,
            "exit": self._handle_exit,
        }

    def process_command(self, user_input: str) -> AssistantResponse:
        """
        Process a user command and return a structured response.

        Args:
            user_input: Raw text from user (typed or recognized from speech)

        Returns:
            AssistantResponse with text and optional action
        """
        if not user_input or not user_input.strip():
            return AssistantResponse(
                text="I didn't catch that. Could you please repeat?",
                action=None
            )

        cleaned = user_input.strip().lower()

        # Check for greetings
        if self._is_greeting(cleaned):
            return self.command_handlers["greeting"](cleaned)

        # Check for exit commands
        if self._is_exit(cleaned):
            return self.command_handlers["exit"](cleaned)

        # Check for help
        if cleaned in ("help", "what can you do", "commands"):
            return self.command_handlers["help"](cleaned)

        # Check for time
        if "time" in cleaned and "date" not in cleaned:
            return self.command_handlers["time"](cleaned)

        # Check for date
        if "date" in cleaned:
            return self.command_handlers["date"](cleaned)

        # Check for joke
        if "joke" in cleaned or "funny" in cleaned:
            return self.command_handlers["joke"](cleaned)

        # Check for open website
        if cleaned.startswith("open "):
            return self.command_handlers["open"](cleaned)

        # Fallback for unknown commands
        return AssistantResponse(
            text=(
                "I'm not sure how to help with that. "
                "Try asking for the time, date, a joke, or say 'open google'. "
                "Say 'help' for more options."
            ),
            action=None
        )

    def _is_greeting(self, text: str) -> bool:
        """Check if input is a greeting."""
        greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
        return any(g in text for g in greetings)

    def _is_exit(self, text: str) -> bool:
        """Check if input is an exit command."""
        exits = ["exit", "quit", "bye", "goodbye", "stop"]
        return any(e in text for e in exits)

    def _handle_help(self, _: str) -> AssistantResponse:
        """Return help text with supported commands."""
        sites = ", ".join(self.ALLOWED_SITES.keys())
        return AssistantResponse(
            text=(
                "I can help you with:\n"
                "• Time — say 'what time is it'\n"
                "• Date — say 'what's today's date'\n"
                "• Jokes — say 'tell me a joke'\n"
                f"• Open websites: {sites} — say 'open google'\n"
                "• Help — say 'help'\n"
                "• Exit — say 'goodbye'\n\n"
                "You can also type commands if speech isn't working."
            ),
            action=None
        )

    def _handle_time(self, _: str) -> AssistantResponse:
        """Return current time."""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        return AssistantResponse(
            text=f"The current time is {time_str}.",
            action="speak_time",
            action_data={"time": time_str}
        )

    def _handle_date(self, _: str) -> AssistantResponse:
        """Return current date."""
        now = datetime.datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        return AssistantResponse(
            text=f"Today is {date_str}.",
            action="speak_date",
            action_data={"date": date_str}
        )

    def _handle_joke(self, _: str) -> AssistantResponse:
        """Return a random programming joke."""
        joke = random.choice(self.JOKES)
        return AssistantResponse(
            text=joke,
            action="tell_joke",
            action_data={"joke": joke}
        )

    def _handle_open(self, text: str) -> AssistantResponse:
        """Open an allowed website."""
        # Extract site name after "open "
        site_key = text.replace("open ", "").strip().lower()

        # Try to match partial site names
        matched_site = None
        for site in self.ALLOWED_SITES:
            if site in site_key or site_key in site:
                matched_site = site
                break

        if matched_site:
            url = self.ALLOWED_SITES[matched_site]
            try:
                webbrowser.open(url)
                return AssistantResponse(
                    text=f"Opening {matched_site.capitalize()} for you.",
                    action="open_url",
                    action_data={"url": url, "site": matched_site}
                )
            except Exception:
                return AssistantResponse(
                    text=f"Sorry, I couldn't open {matched_site}. Please try again.",
                    action=None
                )
        else:
            sites = ", ".join(self.ALLOWED_SITES.keys())
            return AssistantResponse(
                text=f"I can only open these websites: {sites}. Try 'open google' or 'open youtube'.",
                action=None
            )

    def _handle_greeting(self, _: str) -> AssistantResponse:
        """Return a greeting response."""
        hour = datetime.datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        return AssistantResponse(
            text=f"{greeting}! How can I help you today?",
            action="greeting",
            action_data={"greeting": greeting}
        )

    def _handle_exit(self, _: str) -> AssistantResponse:
        """Return exit response."""
        return AssistantResponse(
            text="Goodbye! Have a great day!",
            action="exit",
            action_data=None
        )


def create_assistant() -> VoiceAssistantCore:
    """Factory function to create assistant instance."""
    return VoiceAssistantCore()


if __name__ == "__main__":
    # Quick manual test
    assistant = create_assistant()
    test_commands = [
        "hello",
        "what time is it",
        "what's the date",
        "tell me a joke",
        "open google",
        "open github",
        "open unknownsite",
        "help",
        "goodbye",
        "random unknown command",
    ]
    print("=== Voice Assistant Core Tests ===")
    for cmd in test_commands:
        resp = assistant.process_command(cmd)
        print(f"User: {cmd}")
        print(f"Assistant: {resp.text}")
        if resp.action:
            print(f"  [Action: {resp.action}]")
        print()