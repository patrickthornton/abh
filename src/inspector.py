from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.events import Key
from textual.widget import Widget
from textual.widgets import (
    Label,
    Static,
    Input,
)

import lldb
import struct


class Inspector(Widget):
    """Widget to display the inspector."""

    process: lldb.SBProcess = lldb.SBProcess()
    regs = {}
    dereferencing = False

    def __init__(self, regs: dict) -> None:
        super().__init__()
        self.regs = regs

    def compose(self) -> ComposeResult:
        yield Grid(
            Grid(
                Static("[b green]u8 [/]: ", id="u8", classes="type-spray-cell"),
                Static("[b green]i8 [/]: ", id="i8", classes="type-spray-cell"),
                Static("[b green]f32[/]: ", id="f32", classes="type-spray-cell"),
                Static("[b green]u16[/]: ", id="u16", classes="type-spray-cell"),
                Static("[b green]i16[/]: ", id="i16", classes="type-spray-cell"),
                Static("[b green]f64[/]: ", id="f64", classes="type-spray-cell"),
                Static("[b green]u32[/]: ", id="u32", classes="type-spray-cell"),
                Static("[b green]i32[/]: ", id="i32", classes="type-spray-cell"),
                Static("[b green]str[/]: ", id="str", classes="type-spray-cell"),
                Static("[b green]u64[/]: ", id="u64", classes="type-spray-cell"),
                Static("[b green]i64[/]: ", id="i64", classes="type-spray-cell"),
                Static("[b green]ptr[/]: ", id="ptr", classes="type-spray-cell"),
                Static(
                    "[b magenta]dereferencing[/]: [b i]no[/]",
                    id="drf",
                    classes="type-spray-cell",
                ),
                id="type-spray",
            ),
            Grid(
                Label("examinee:"),
                Static(id="hex"),
                Input("", placeholder="examinee", id="examinee"),
                id="inspector-input",
            ),
            id="inspector",
        )

    @on(Input.Submitted)
    def parse(self, event: Input.Submitted) -> None:
        if not event.value:
            return

        hex_static = self.query_one("#hex", Static)
        if not self.regs:
            hex_static.update("[i red]no process running[/]")
            return

        # convert, say, 'rax' to '0x000ff...'
        input = event.value.lower()
        for reg, value in self.regs.items():
            input = input.replace(reg, value)

        # check for validity, roughly
        for char in input:
            if char not in "0123456789abcdefx+-*":
                hex_static.update("[i red]invalid input[/]")
                return

        # eval; SECURITY RISK !!
        try:
            output = eval(input)
        except Exception as _:
            hex_static.update("[i red]address parse failure[/]")
            return

        if not isinstance(output, int):
            hex_static.update("[i red]address parse failure[/]")
            return

        if output < 0:
            hex_static.update("[i red]negative address[/]")
            return

        hex_static.update(f"{event.value}:\n[b blue]0x{output:016x}[/]")

        self.type_spray(f"{output:016x}", self.dereferencing)

    def update(self, process: lldb.SBProcess, regs: dict) -> None:
        self.process = process
        self.regs = regs
        self.reload()

    # address will be 16 characters long, and will have no 0x
    def type_spray(self, address: str, dereferencing: bool) -> None:
        if not self.process:
            return

        addr = int(address, 16)
        error = lldb.SBError()
        data: bytes

        drf = self.query_one("#drf", Static)
        if dereferencing:
            data = self.process.ReadMemory(addr, 16, error)
            if error.Fail():
                drf.update(
                    "[b magenta]dereferencing[/]: [b i]yes[/]; [i red]but dereference failed[/]"
                )

                # wipe entries
                type_spray = {}
                for key in [
                    "u8",
                    "u16",
                    "u32",
                    "u64",
                    "i8",
                    "i16",
                    "i32",
                    "i64",
                    "f32",
                    "f64",
                    "str",
                    "ptr",
                ]:
                    type_spray[key] = ""
                for key, value in type_spray.items():
                    self.query_one(f"#{key}", Static).update(
                        f"[b green]{key}[/]: {value}"
                    )
                return

            drf.update(
                f"[b magenta]dereferencing[/]: [b i]yes[/]; results are from [b blue]0x{int.from_bytes(data[-8:], 'big'):016x}[/]"
            )
        else:
            # convert hex string to byte array
            data = bytes.fromhex(address)
            drf.update("[b magenta]dereferencing[/]: [b i]no[/]")

        # the 'big's here are an artifact of the fromhex() above
        type_spray = {}
        type_spray["u8"] = int.from_bytes(data[:1], "big", signed=False)
        type_spray["u16"] = int.from_bytes(data[:2], "big", signed=False)
        type_spray["u32"] = int.from_bytes(data[:4], "big", signed=False)
        type_spray["u64"] = int.from_bytes(data[:8], "big", signed=False)
        type_spray["i8"] = int.from_bytes(data[:1], "big", signed=True)
        type_spray["i16"] = int.from_bytes(data[:2], "big", signed=True)
        type_spray["i32"] = int.from_bytes(data[:4], "big", signed=True)
        type_spray["i64"] = int.from_bytes(data[:8], "big", signed=True)
        type_spray["f32"] = struct.unpack("f", data[:4])[0]
        type_spray["f64"] = struct.unpack("d", data[:8])[0]

        type_spray["str"] = data.decode("ascii", errors="ignore")

        # this threw internal errors?
        # string = self.process.ReadCStringFromMemory(addr, 256, error)
        # if error.Success():
        #     type_spray['str'] = string
        # else:
        #     type_spray['str'] = "[i red]n/a[/]"

        ptr = self.process.ReadPointerFromMemory(addr, error)
        if error.Success():
            type_spray["ptr"] = ptr
        else:
            type_spray["ptr"] = "[i red]n/a[/]"

        for key, value in type_spray.items():
            self.query_one(f"#{key}", Static).update(f"[b green]{key}[/]: {value}")

    def deref_toggle(self) -> None:
        self.dereferencing = not self.dereferencing
        self.reload()

    def reload(self) -> None:
        # mimic submission of input
        input = self.query_one("#examinee", Input)
        self.parse(Input.Submitted(input, input.value))

    def input_focus(self) -> None:
        self.query_one("#examinee", Input).focus()

    @on(Key)
    def esc(self, event: Key) -> None:
        if event.key == "escape":
            self.query_one("#examinee", Input).blur()
