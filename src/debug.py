#!/usr/bin/env python

import lldb
import os

def disassemble_instructions(insts):
    for i in insts:
        print(i)

# Set the path to the executable to debug
exe = "test/hello"

# Create a new debugger instance
debugger = lldb.SBDebugger.Create()

# When we step or continue, don't return from the function until the process
# stops. Otherwise we would have to handle the process events ourselves which, while doable is
#a little tricky.  We do this by setting the async mode to false.
debugger.SetAsync(False)

# Create a target from a file and arch
print(f"Creating a target for {exe}...")

target = debugger.CreateTarget(exe)

if target:
    # If the target is valid set a breakpoint at main
    main_bp = target.BreakpointCreateByName("main", target.GetExecutable().GetFilename());

    print(main_bp)

    # Launch the process. Since we specified synchronous mode, we won't return
    # from this function until we hit the breakpoint at main
    process = target.LaunchSimple(None, None, os.getcwd())

    # Make sure the launch went ok
    if process:
        # Print some simple process info
        state = process.GetState()
        print(process)
        if state == lldb.eStateStopped:
            # Get the first thread
            thread = process.GetThreadAtIndex(0)
            if thread:
                # Print some simple thread info
                print(thread)
                # Get the first frame
                frame = thread.GetFrameAtIndex(0)
                if frame:
                    # Print some simple frame info
                    print(frame)
                    function = frame.GetFunction()
                    # See if we have debug info (a function)
                    if function:
                        # We do have a function, print some info for the function
                        print(function)
                        # Now get all instructions for this function and print them
                        insts = function.GetInstructions(target)
                        disassemble_instructions(insts)
                    else:
                        # See if we have a symbol in the symbol table for where we stopped
                        symbol = frame.GetSymbol();
                        if symbol:
                            # We do have a symbol, print some info for the symbol
                            print(symbol)
                            insts = symbol.GetInstructions(target)
                            disassemble_instructions(insts)

#kyra trying to figure stuff out :(

res = lldb.SBCommandReturnObject()
ci = debugger.GetCommandInterpreter()
def __lldb_init_module(debugger, internal_dict):
    ci.HandleCommand("command script add -f lldbinit.cmd_xt newcmd", res)

#https://nusgreyhats.org/posts/writeups/basic-lldb-scripting/
#to print unicode strings from memory (similar to x/s but printing unicode strings)
def cmd_xt(debugger, command, result, _dict):
    args = command.split(' ')
    if len(args) < 1:
        print('xt <expression>')
        return

    addr = int(thread.GetFrameAtIndex(0).EvaluateExpression(args[0]).GetValue(), 10)
    error = lldb.SBError()

    ended = False
    s = u''
    offset = 0

    while not ended:
        mem = target.GetProcess().ReadMemory(addr + offset, 100, error)
        for i in range(0, 100, 2):
            wc = mem[i+1] << 8 | mem[i]
            s += chr(wc)
            if wc == 0:
                ended = True
                break

        offset += 100

    print(s)
