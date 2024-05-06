from textual.app import ComposeResult
from textual.containers import Grid
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import (
    Label,
)

import lldb


class SessionInfo(Widget):
    """Display current target and process information at the bottom."""

    filename: reactive[str] = reactive("")
    target: reactive[lldb.SBTarget] = reactive(lldb.SBTarget())
    process: reactive[lldb.SBProcess] = reactive(lldb.SBProcess())
    thread: reactive[lldb.SBThread] = reactive(lldb.SBThread())
    mounted: bool = False

    def compose(self) -> ComposeResult:
        yield Grid(
            Grid(
                Label("[b]target[/b]", classes="session-label"),
                Label("", id="target", classes="session-contents"),
                classes="session-item",
            ),
            Grid(
                Label("[b]process[/b]", classes="session-label"),
                Label("", id="process", classes="session-contents"),
                classes="session-item",
            ),
            Grid(
                Label("[b]thread[/b]", classes="session-label"),
                Label("", id="thread", classes="session-contents"),
                classes="session-item",
            ),
            id="session-info",
        )

    def on_mount(self) -> None:
        self.mounted = True

    def watch_target(self, target: lldb.SBTarget) -> None:
        if not self.mounted:
            return
        if target:
            message = f"filename: [i red]{target}[/i red]"
        else:
            message = "[bright_black]no target selected[/bright_black]"
        self.query_one("#target", Label).update(message)

    def watch_process(self, process: lldb.SBProcess) -> None:
        if not self.mounted:
            return
        if process:
            desc = str(process).replace("SBProcess: ", "")
            desc_parts = desc.split(", ")
            pid = desc_parts[0].split(" = ")[1]
            state = desc_parts[1].split(" = ")[1]
            message = f"process ID: [b green]{pid}[/] is [b green]{state}[/]"
        else:
            message = "[bright_black]no process running[/bright_black]"
        self.query_one("#process", Label).update(message)

    def watch_thread(self, thread: lldb.SBThread) -> None:
        if not self.mounted:
            return
        if thread:
            desc = thread.GetStopDescription(1000)
            if desc:
                message = f"at [purple]{desc}[/purple]"
            else:
                message = "[purple]exited[/purple]"
        else:
            message = "[bright_black]thread not stopped[/bright_black]"
        self.query_one("#thread", Label).update(message)

    def update(
        self, target: lldb.SBTarget, process: lldb.SBProcess, thread: lldb.SBThread
    ) -> None:
        self.watch_target(target)
        self.watch_process(process)
        self.watch_thread(thread)
