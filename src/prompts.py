from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import (
    Input,
    Label,
    RichLog,
)

import lldb


class Prompt(ModalScreen[str]):
    @on(Input.Submitted)
    def set_target(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    @on(Key)
    def esc(self, event: Key) -> None:
        if event.key == "escape":
            self.dismiss("\n")


class TargetPrompt(Prompt):
    """Prompt for setting the target."""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("input the target executable", id="t-label"),
            Input("", placeholder="name of target executable", id="t-path"),
            id="t-grid",
            classes="modal",
        )


class BreakpointPrompt(Prompt):
    """Prompt for setting the breakpoint."""

    breakpoints: list[lldb.SBBreakpoint] = []

    def __init__(self, breakpoints: list[lldb.SBBreakpoint]) -> None:
        super().__init__()
        self.breakpoints = breakpoints

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("[b]existing breakpoints:"),
            RichLog(id="bs", classes="scroller", markup=True),
            Label("input the name of the symbol to break at", id="b-label"),
            Input("", placeholder="name of symbol to break at", id="b-path"),
            id="b-grid",
            classes="big-modal",
        )

    def on_mount(self) -> None:
        self.query_one("#b-path", Input).focus()
        bs = self.query_one("#bs", RichLog)
        bs.clear()

        for bp in self.breakpoints:
            bp_str = str(bp).replace("SBBreakpoint: ", "")
            bp_parts = bp_str.split(", ")
            id = bp.id
            name = bp_parts[1].split(" ")[2]
            locations = bp.num_locations
            bs.write(
                f" [b cyan]{id}[/]: name = [green]{name}[/], locations = [b magenta]{locations}[/]"
            )


class ExaminePrompt(Prompt):
    """Prompt for examining memory."""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("input the address you want to examine", id="x-label"),
            Input("", placeholder="address to examine in hexadecimal", id="x-path"),
            id="x-grid",
            classes="modal",
        )
