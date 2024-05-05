"""
Code browser example.

Run with:

    python code_browser.py PATH
"""

import sys

from rich.syntax import Syntax
from rich.traceback import Traceback

from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.reactive import var
from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Footer, Header, Input, Static

import lldb
import os

class CodeBrowser(App):
    """Textual code browser app."""

    CSS_PATH = "abh.css"
    BINDINGS = [
        ("t", "set_target", "Set Target"),
        ("q", "quit", "Quit"),
    ]

    dbg = lldb.SBDebugger.Create()
    dbg.SetAsync(False)

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        yield Header()
        with Container():
            with VerticalScroll(id="code-view"):
                yield Static(id="code", expand=True)
        yield Footer()

    def on_mount(self) -> None:
        pass

    def action_set_target(self) -> None:
        """Set the target."""
        self.push_screen(TargetPrompt())

class TargetPrompt(ModalScreen):
    """Prompt for setting the target."""

    def compose(self) -> ComposeResult:
        yield Input("", id="target-path")

if __name__ == "__main__":
    CodeBrowser().run()
