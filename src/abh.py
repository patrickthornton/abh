"""
Textual Terminal example.

Run with:

    python abh.py PATH
"""

import sys

from rich.syntax import Syntax
from rich.traceback import Traceback
from textual import on, log, work
from textual.app import App, ComposeResult
from textual.containers import Container, Grid
from textual.events import Key
from textual.message import Message
from textual.reactive import reactive, var
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import DirectoryTree, Footer, Header, Input, Static, Label, Button, RichLog
from textual.validation import Function, Number, ValidationResult, Validator

import lldb
import os

class OurDebugger(App):
    """Textual code browser app."""

    CSS_PATH = "abh.css"
    BINDINGS = [
        ("t", "target", "target"),
        ("r", "run", "run"),
        ("c", "continue", "continue"),
        ("b", "breakpoint", "breakpoint"),
        ("s", "step", "step"),
        ("n", "next", "next"),
        ("q", "quit", "quit"),
    ]

    dbg: reactive[lldb.SBDebugger] = reactive(lldb.SBDebugger.Create())
    filename: reactive[str] = reactive("")
    target: reactive[lldb.SBTarget] = reactive(lldb.SBTarget())
    process: reactive[lldb.SBProcess] = reactive(lldb.SBProcess())

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        yield Header()
        with Container():
            yield SessionInfo().data_bind(OurDebugger.dbg, OurDebugger.filename, OurDebugger.target, OurDebugger.process)
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Our Debugger!! <3"
        self.dbg.SetAsync(False)

    def action_target(self) -> None:
        """Set the target."""

        def set_target(path: str) -> None:
            target = self.dbg.CreateTarget(path)
            if not target:
                self.error("couldn't find executable with that name!")
                return

            self.target = target
            self.filename = target.GetExecutable().GetFilename()

        self.push_screen(TargetPrompt(), set_target)

    def action_run(self) -> None:
        """Run the target."""

        if not self.target:
            self.error("no target set!")
            return

        process = self.target.LaunchSimple(None, None, os.getcwd())
        if not process:
            self.error("couldn't launch process!")
            return

        self.process = process


    def action_breakpoint(self) -> None:
        """Set a breakpoint."""

        def set_breakpoint(path: str) -> None:
            if self.target:
                breakpoint = self.target.BreakpointCreateByName(path, self.filename)
                if breakpoint:
                    log(breakpoint)
                    return
            log("no breakpoint set")

        self.push_screen(BreakpointPrompt(), set_breakpoint)

    def action_continue(self) -> None:
        """Continue stepping until the next breakpoint."""

        if self.process:
            process = self.process.Continue()
            if process:
                log(self.process)

    def action_step(self) -> None:
        """Step one instruction, stepping into function calls."""
        self.step(False)

    def action_next(self) -> None:
        """Step one instruction, stepping over function calls."""
        self.step(True)

    def step(self, step_over: bool) -> None:
        """Continue onto the next line, stepping over"""

        if not self.process:
            return

        state = self.process.GetState()
        if state == lldb.eStateStopped:
            thread = self.process.GetThreadAtIndex(0)
            thread.StepInstruction(step_over)
            log(thread)

    def error(self, message: str) -> None:
        """Display an error message."""
        self.push_screen(ErrorScreen(message))

class SessionInfo(Widget):
    """Display current target and process information at the bottom."""

    dbg: reactive[lldb.SBDebugger] = reactive(lldb.SBDebugger.Create())
    filename: reactive[str] = reactive("")
    target: reactive[lldb.SBTarget] = reactive(lldb.SBTarget())
    process: reactive[lldb.SBProcess] = reactive(lldb.SBProcess())
    mounted: bool = False

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("", id="target", classes="session-item"),
            Label("", id="process", classes="session-item"),
            id="session-info"
        )

    def on_mount(self) -> None:
        self.mounted = True

    def watch_target(self, target: lldb.SBTarget) -> None:
        if not self.mounted:
            return
        if target:
            message = f"target: {target}"
        else:
            message = "no target selected"
        self.query_one("#target", Label).update(message)

    def watch_process(self, process: lldb.SBProcess) -> None:
        if not self.mounted:
            return
        if process:
            message = f"process: {process}"
        else:
            message = "no process running"
        self.query_one("#process", Label).update(message)

class TargetPrompt(ModalScreen[str]):
    """Prompt for setting the target."""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("input the target executable", id="t-label"),
            Input("", placeholder="name of target executable", id="t-path"),
            id="t-grid")

    @on(Input.Submitted)
    def set_target(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

class BreakpointPrompt(ModalScreen[str]):
    """Prompt for setting the breakpoint."""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("input the name of the symbol to break at", id="b-label"),
            Input("", placeholder="name of symbol to break at", id="b-path"),
            id="b-grid")

    @on(Input.Submitted)
    def set_breakpoint(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

class ErrorScreen(ModalScreen[str]):
    """Display an error message."""

    message: str = "there was an error!"

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("action failed:", id="error-label"),
            Label(self.message),
            id="error-message")

    @on(Key)
    def begone(self) -> None:
        self.dismiss()

if __name__ == "__main__":
    OurDebugger().run()
