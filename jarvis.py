#!/usr/bin/env python3
"""
J.A.R.V.I.S. — Just A Rather Very Intelligent System
A terminal-based AI assistant inspired by Tony Stark's JARVIS.
"""

import os
import sys
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional; variables can be set in the environment directly

try:
    from openai import OpenAI, APIConnectionError, APIStatusError, APITimeoutError
except ImportError:
    print("Error: 'openai' package is not installed.")
    print("Run:  pip install -r requirements.txt")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.rule import Rule
    from rich.prompt import Prompt
    from rich import print as rprint
    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), the AI assistant \
created by Tony Stark. You are highly intelligent, articulate, and unfailingly \
helpful. You speak with refined British diction, address the user as "Sir" or \
"Ma'am", and provide precise, thorough responses. You are capable of assisting \
with any task — technical problems, research, writing, analysis, or casual \
conversation — and you do so with calm confidence and a subtle wit. \
Never break character.\
"""

BANNER = r"""
     ___  ________  ________  ___      ___ ___  ________
    |\  \|\   __  \|\   __  \|\  \    /  /|\  \|\   ____\
    \ \  \ \  \|\  \ \  \|\  \ \  \  /  / | \  \ \  \___|
  __ \ \  \ \   __  \ \   _  _\ \  \/  / / \ \  \ \_____  \
 |\  \\_\  \ \  \ \  \ \  \\  \\ \    / /   \ \  \|____|\  \
 \ \________\ \__\ \__\ \__\\ _\\ \__/ /     \ \__\____\_\  \
  \|________|\|__|\|__|\|__|\|__|\|__|/       \|__|\_________\
                                                   \|_________|
  J.A.R.V.I.S. — Just A Rather Very Intelligent System
"""

HELP_TEXT = """
[bold cyan]Available commands[/bold cyan]

  [green]help[/green]      Show this help message
  [green]clear[/green]     Clear conversation history (start a fresh session)
  [green]history[/green]   Print the current conversation history
  [green]exit[/green]      Exit JARVIS  (also: quit / bye)

  Anything else is sent directly to JARVIS as a message.
"""

# Placeholder API key used when connecting to local endpoints (e.g. Ollama)
# that do not require authentication.
_LOCAL_ENDPOINT_PLACEHOLDER_KEY = "local-endpoint"
DEFAULT_MODEL = "gpt-4o-mini"
MAX_HISTORY_MESSAGES = 40  # keep last N user+assistant pairs in context


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _get_client() -> OpenAI:
    """Create and return an OpenAI client."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("OPENAI_BASE_URL", "")  # optional: Ollama / custom endpoint

    if not api_key and not base_url:
        raise EnvironmentError(
            "OPENAI_API_KEY is not set.\n"
            "Set it in a .env file or as an environment variable.\n"
            "See .env.example for details."
        )

    kwargs: dict = {"api_key": api_key or _LOCAL_ENDPOINT_PLACEHOLDER_KEY}  # local endpoints don't need a real key
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def _model_name() -> str:
    return os.environ.get("JARVIS_MODEL", DEFAULT_MODEL)


def _timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# Terminal I/O — with graceful fallback when Rich is not installed
# ---------------------------------------------------------------------------

class _TerminalIO:
    def __init__(self) -> None:
        self.console = Console() if _RICH_AVAILABLE else None

    def print_banner(self) -> None:
        if self.console:
            self.console.print(BANNER, style="bold cyan")
            self.console.print(Rule(style="cyan"))
            self.console.print(
                f"[dim]Model: {_model_name()} | Type [bold]help[/bold] for commands[/dim]\n"
            )
        else:
            print(BANNER)
            print("-" * 60)
            print(f"Model: {_model_name()} | Type 'help' for commands\n")

    def print_help(self) -> None:
        if self.console:
            self.console.print(Panel(HELP_TEXT, title="JARVIS Help", border_style="cyan"))
        else:
            print(
                "\nAvailable commands: help, clear, history, exit / quit / bye\n"
                "Anything else is sent to JARVIS.\n"
            )

    def user_input(self) -> str:
        if self.console:
            return Prompt.ask("[bold yellow]You[/bold yellow]").strip()
        return input("You: ").strip()

    def print_jarvis(self, text: str) -> None:
        if self.console:
            self.console.print(
                Panel(
                    Text(text),
                    title=f"[bold cyan]JARVIS[/bold cyan] [dim]{_timestamp()}[/dim]",
                    border_style="cyan",
                    padding=(0, 1),
                )
            )
        else:
            print(f"\nJARVIS [{_timestamp()}]: {text}\n")

    def print_info(self, text: str) -> None:
        if self.console:
            self.console.print(f"[dim]{text}[/dim]")
        else:
            print(text)

    def print_error(self, text: str) -> None:
        if self.console:
            self.console.print(f"[bold red]Error:[/bold red] {text}")
        else:
            print(f"Error: {text}", file=sys.stderr)

    def print_history(self, messages: list) -> None:
        if not messages:
            self.print_info("Conversation history is empty.")
            return
        for msg in messages:
            role = msg["role"].upper()
            content = msg["content"]
            if self.console:
                color = "yellow" if role == "USER" else "cyan"
                self.console.print(f"[bold {color}]{role}:[/bold {color}] {content}\n")
            else:
                print(f"{role}: {content}\n")


# ---------------------------------------------------------------------------
# Core chat logic
# ---------------------------------------------------------------------------

class Jarvis:
    def __init__(self) -> None:
        self.client = _get_client()
        self.model = _model_name()
        self.history: list[dict] = []
        self.io = _TerminalIO()

    def _build_messages(self) -> list[dict]:
        """Construct the message list sent to the API."""
        trimmed = self.history[-MAX_HISTORY_MESSAGES:]
        return [{"role": "system", "content": SYSTEM_PROMPT}] + trimmed

    def chat(self, user_message: str) -> str:
        """Send a message and return JARVIS's response."""
        self.history.append({"role": "user", "content": user_message})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self._build_messages(),
        )
        reply = response.choices[0].message.content or ""
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def clear_history(self) -> None:
        self.history.clear()
        self.io.print_info("Conversation history cleared.")

    def run(self) -> None:
        """Start the interactive JARVIS terminal session."""
        self.io.print_banner()

        while True:
            try:
                user_input = self.io.user_input()
            except (KeyboardInterrupt, EOFError):
                print()
                self.io.print_info("Goodbye, Sir.")
                break

            if not user_input:
                continue

            command = user_input.lower()

            if command in ("exit", "quit", "bye"):
                self.io.print_info("Goodbye, Sir.")
                break

            if command == "help":
                self.io.print_help()
                continue

            if command == "clear":
                self.clear_history()
                continue

            if command == "history":
                self.io.print_history(self.history)
                continue

            # Send to AI
            try:
                reply = self.chat(user_input)
                self.io.print_jarvis(reply)
            except EnvironmentError as exc:
                self.io.print_error(str(exc))
                break
            except APIConnectionError as exc:
                self.io.print_error(
                    f"Could not connect to the API. Check your network or OPENAI_BASE_URL. ({exc})"
                )
            except APITimeoutError:
                self.io.print_error("The API request timed out. Please try again.")
            except APIStatusError as exc:
                self.io.print_error(
                    f"API returned an error (HTTP {exc.status_code}): {exc.message}"
                )
            except Exception as exc:  # noqa: BLE001
                self.io.print_error(f"Unexpected error: {exc}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    try:
        jarvis = Jarvis()
        jarvis.run()
    except EnvironmentError as exc:
        if _RICH_AVAILABLE:
            Console().print(f"[bold red]Configuration error:[/bold red] {exc}")
        else:
            print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
