from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import (
    Label,
)


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
            id="error-message",
            classes="modal",
        )

    @on(Key)
    def begone(self) -> None:
        self.dismiss()
