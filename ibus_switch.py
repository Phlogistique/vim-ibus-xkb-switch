#!/usr/bin/env python2
from sys import argv, stderr
from os.path import exists
from os import remove
import ibus

# SLOWWWWWW I'M PRETTY SURE THIS IS TOO SLOWWWWWWWWWWW
# I wrote it in Python because I don't understand D-BUS very well but I'm
# pretty sure it would be ten times faster just launching qdbus from the shell.
# Wouldn't it?

# This is expected to be used in .vimrc like this:
#
#     au InsertEnter * call system("$HOME/.vim/ibus_switch/ibus_switch.py enable /tmp/vim_im." . getpid())
#     au InsertLeave * call system("$HOME/.vim/ibus_switch/ibus_switch.py disable /tmp/vim_im." . getpid())
#
# /!\ ERRORS ARE SILENT. Test those outside VIM first. It might also be better
# if you execute them using the python bindings in VIM. However for some reason
# it will crash if you try to do that in Arch Linux.
# 
# You might also want to redraw! after every InsertEnter and InsertLeave
# because for some reason if you type something in the terminal while the
# script is SUPER SLOWWWWLY running it will get displayed to the screen and
# then won't get cleaned up.
#
#     au InsertEnter,InsertLeave * redraw!

# I should make it a real VIM plugin because it is genuinely useful to anyone
# using vim with ibus-xkb plus a Japanese or Chinese input method. I'm pretty
# sure I'm not the only one, it looks like it's the only viable way to get a
# complex input method AND dead keys working in XIM apps.

# This is a quite horrible hack because I need the XKB input method to emulate
# input without IBus, in order to workaround the 'no dead keys in XIM apps'
# bug. Therefore, instead of enabling/disabling the input method,
# "disable" saves the current input method to a file and sets the input method
# to DISABLED_ENGINE while "enable" restores the input method from the file.
DISABLED_ENGINE = "xkb:layout:fr"

bus = ibus.bus.Bus()
ic = ibus.inputcontext.InputContext(bus, bus.current_input_contxt())
if not ic.is_enabled():
    print >>stderr, ("WARNING: IBus not enabled, enabling. " +
                     "This seems to often lead to a race condition. " +
                     "I don't even want to know.")
    ic.enable()

class EngineHack:
    # seen in ibus/inputcontext.py:
    #
    #     def set_engine(self, engine):
    #         return self.__context.SetEngine(engine.name)
    #
    # The correct behaviour would be retrieving a list of engines from
    # Bus.engines_list or something but then saving and retrieving the state
    # would become a hassle.

    def __init__(self, name): self.name = name

class BadArgs: pass

try:
    if len(argv) < 3:
        raise BadArgs()

    if argv[1] == "enable":
        if exists(argv[2]):
            with open(argv[2], 'r') as f:
                ic.set_engine(EngineHack(f.read()))

            # remove(argv[2]) 
            # I would do this but I don't want this script to delete random
            # files so I can live with gajillions of files all containing
            # xkb:layout:fr

    elif argv[1] == "disable":
        with open(argv[2], 'w') as f:
            f.write(ic.get_engine().name)
        ic.set_engine(EngineHack(DISABLED_ENGINE))
    else:
        raise BadArgs()

except BadArgs:
    print >>stderr, "Use: %s enable|disable <filename>" % argv[0]
    engine = ic.get_engine()
    if engine:
        print >>stderr, "Current engine: %s" % engine.name

