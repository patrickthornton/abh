from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import (
    Label,
    RichLog,
)


class Notif(ModalScreen[str]):
    @on(Key)
    def begone(self) -> None:
        self.dismiss()


class SymbolNotif(Notif):
    """Display the symbols found in the target."""

    symbols: list[str] = []

    def __init__(self, symbols: list[str]) -> None:
        super().__init__()
        self.symbols = symbols

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("[b]symbols found in target:"),
            RichLog(id="symbols", markup=True, classes="scroller"),
            classes="big-modal",
        )

    def on_mount(self) -> None:
        symbols = self.query_one("#symbols", RichLog)
        symbols.clear()

        for symbol in self.symbols:
            symbol_parts = symbol.split(", ")
            id = int(
                symbol_parts[0].split(" = ")[1].replace("{", "").replace("}", ""), 16
            )
            range = symbol_parts[1].split(" = ")[1]
            name = symbol_parts[2].split("=")[1]
            symbols.write(f" [b cyan]{id}[/]: from [blue]{range}[/]; [green]{name}[/]")


class ErrorNotif(Notif):
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


class WarningMotif(Notif):
    """Display a warning message."""

    message: str = "there was a warning!"

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("warning:", id="error-label"),
            Label(self.message),
            id="warning-message",
            classes="modal",
        )
