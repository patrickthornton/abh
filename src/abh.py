"""
american bunny hop; a tui wrapper for lldb.

Run with:

    python abh.py
"""

from rich.syntax import Syntax
from textual import log
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.reactive import reactive
from textual.widgets import (
    Footer,
    Header,
    RichLog,
)

import lldb
import os
import re

from sessioninfo import SessionInfo
from prompts import TargetPrompt, BreakpointPrompt, ExaminePrompt
from notifs import ErrorNotif, SymbolNotif, WarningMotif


class AmericanBunnyHop(App):
    """american bunny hop."""

    CSS_PATH = "abh.css"
    BINDINGS = [
        ("t", "target", "target"),
        ("s", "symbols", "symbols"),
        ("b", "breakpoint", "breakpoint"),
        ("r", "run", "run"),
        ("c", "continue", "continue"),
        ("o", "step", "step over"),
        ("i", "next", "step into"),
        ("x", "examine", "examine"),
        ("q", "clean_quit", "quit"),
    ]

    dbg: reactive[lldb.SBDebugger] = reactive(lldb.SBDebugger.Create())
    filename: reactive[str] = reactive("")
    target: reactive[lldb.SBTarget] = reactive(lldb.SBTarget())
    process: reactive[lldb.SBProcess] = reactive(lldb.SBProcess())
    thread: reactive[lldb.SBThread] = reactive(lldb.SBThread())
    mounted: bool = False
    regex = re.compile(r"\[[0-9]+m")
    previous_regs = {}

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        yield Header()
        yield Grid(
            SessionInfo().data_bind(
                AmericanBunnyHop.filename,
                AmericanBunnyHop.target,
                AmericanBunnyHop.process,
                AmericanBunnyHop.thread,
            ),
            Grid(
                RichLog(
                    id="regs64",
                    auto_scroll=False,
                    markup=True,
                    classes="regs_item scroller",
                ),
                RichLog(
                    id="regs32",
                    auto_scroll=False,
                    markup=True,
                    classes="regs_item scroller",
                ),
                RichLog(
                    id="regs16",
                    auto_scroll=False,
                    markup=True,
                    classes="regs_item scroller",
                ),
                RichLog(
                    id="regs8",
                    auto_scroll=False,
                    markup=True,
                    classes="regs_item scroller",
                ),
                id="regs",
            ),
            RichLog(id="inspector", classes="scroller", auto_scroll=False),
            RichLog(id="asm", classes="scroller", auto_scroll=False),
            id="body",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.title = "american bunny hop"
        self.dbg.SetAsync(False)
        self.mounted = True

        # SCRAP THESE LINES LATER
        target = self.dbg.CreateTarget("test/hello")
        self.target = target
        self.filename = target.GetExecutable().GetFilename()

    def action_target(self) -> None:
        """Set the target."""

        def set_target(path: str) -> None:
            # handle escape
            if path == "\n":
                return

            target = self.dbg.CreateTarget(path)
            if not target:
                self.error("couldn't find executable with that name!")
                return

            self.target = target
            self.filename = target.GetExecutable().GetFilename()

        self.push_screen(TargetPrompt(), set_target)

    def action_symbols(self) -> None:
        """List symbols in the target."""

        if not self.target:
            self.error("no target set!")
            return

        symbols = []
        for module in self.target.module_iter():
            if self.filename not in str(module):
                continue
            for symbol in module:
                if "mangled" in str(symbol):
                    continue
                symbols.append(str(symbol))

        self.push_screen(SymbolNotif(symbols))

    def action_breakpoint(self) -> None:
        """Set a breakpoint."""

        breakpoints = list(self.target.breakpoint_iter())
        breakpoint_names = [
            str(breakpoint).split(", ")[1].split(" = ")[1][1:-1]
            for breakpoint in breakpoints
        ]

        def set_breakpoint(path: str) -> None:
            # handle escape
            if path == "\n":
                return

            if not self.target:
                self.error("no target set!")
                return

            # check for duplicates
            log(breakpoint_names)
            if path in breakpoint_names:
                self.error("breakpoint already set!")
                return

            breakpoint = self.target.BreakpointCreateByName(path, self.filename)
            log(breakpoint)
            if not breakpoint:
                self.error("couldn't set breakpoint!")
                return

            # warn if 0 locations
            if breakpoint.GetNumLocations() == 0:
                self.warn("no locations found for breakpoint")
                return

        self.push_screen(BreakpointPrompt(breakpoints), set_breakpoint)

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
        self.thread = process.GetSelectedThread()
        self.disas()

    def action_continue(self) -> None:
        """Continue stepping until the next breakpoint."""

        if not self.process:
            self.error("no process running!")
            return

        process = self.process.Continue()
        if not process:
            self.error("couldn't continue process!")
            return

        self.disas()

    def action_step(self) -> None:
        """Step one instruction, stepping into function calls."""
        self.step(False)

    def action_next(self) -> None:
        """Step one instruction, stepping over function calls."""
        self.step(True)

    def step(self, step_over: bool) -> None:
        """Continue onto the next line, stepping over"""

        if not self.process:
            self.error("no process running!")
            return
        if not self.process.GetState() == lldb.eStateStopped:
            self.error("process not stopped!")
            return
        if not self.thread:
            self.error("no thread selected!")
            return

        self.thread.StepInstruction(step_over)
        self.disas()

    def action_examine(self) -> None:
        """Examine a memory address."""

        def examine(address: str) -> None:
            # handle escape
            if address == "\n":
                return

            if not self.process:
                self.error("no process running!")
                return

            inspector = self.query_one("#inspector", RichLog)

            error = lldb.SBError()
            addr = int(address, 16)
            data = self.process.ReadMemory(addr, 16, error)
            if error.Fail():
                self.error("couldn't read memory!")
                return

            hexdump = Syntax(
                data.hex(), "ecl", line_numbers=True, background_color="#1e1e1e"
            )

            inspector.clear()
            inspector.write(hexdump)

        self.push_screen(ExaminePrompt(), examine)

    def action_clean_quit(self) -> None:
        if self.process:
            self.process.Destroy()
        self.app.exit()

    # manages assembly view and regs view
    def disas(self) -> None:
        # update regs and session info, too
        self.regs()
        self.update_session_info()

        if not self.mounted or not self.process or not self.thread:
            return

        state = self.process.GetState()
        richlog = self.query_one("#asm", RichLog)
        if state == lldb.eStateExited:
            richlog.clear()
            richlog.write(" process exited!")
            return
        if state != lldb.eStateStopped:
            return

        frame: lldb.SBFrame = self.thread.GetSelectedFrame()
        if not frame:
            return

        disas = frame.Disassemble()

        # peel off extra characters
        disas = self.regex.sub("", disas)

        # prettify
        asm = Syntax(disas, "ecl", line_numbers=True, background_color="#1e1e1e")

        # write to the screen
        richlog.clear()
        richlog.write(asm)

    def regs(self) -> None:
        if (
            not self.mounted
            or not self.process
            or self.process.GetState() != lldb.eStateStopped
            or not self.thread
        ):
            return

        frame: lldb.SBFrame = self.thread.GetSelectedFrame()
        if not frame:
            return
        log64 = self.query_one("#regs64", RichLog)
        log32 = self.query_one("#regs32", RichLog)
        log16 = self.query_one("#regs16", RichLog)
        log8 = self.query_one("#regs8", RichLog)
        log64.clear()
        log32.clear()
        log16.clear()
        log8.clear()

        regs = frame.GetRegisters()
        gprs = []
        for reg in regs:
            if "general purpose registers" in reg.name.lower():
                gprs = reg
                break
        for reg in gprs:
            if len(reg.value) == 4:
                richlog = log8
            elif len(reg.value) == 6:
                richlog = log16
            elif len(reg.value) == 10:
                richlog = log32
            elif len(reg.value) == 18:
                richlog = log64
            else:
                richlog = log8

            if (
                reg.name in self.previous_regs
                and reg.value != self.previous_regs[reg.name]
            ):
                richlog.write(f"[magenta]%[/]{reg.name: <6}: [blue b r]{reg.value}[/]")
            else:
                richlog.write(f"[magenta]%[/]{reg.name: <6}: [blue]{reg.value}[/]")
            self.previous_regs[reg.name] = reg.value

    def update_session_info(self) -> None:
        self.query_one(SessionInfo).update(self.target, self.process, self.thread)

    def error(self, message: str) -> None:
        """Display an error message."""
        self.push_screen(ErrorNotif(message))

    def warn(self, message: str) -> None:
        """Display a warning message."""
        self.push_screen(WarningMotif(message))


if __name__ == "__main__":
    AmericanBunnyHop().run()
