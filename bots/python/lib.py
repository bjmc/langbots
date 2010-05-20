#!/usr/bin/python
import sys
import math
import random
import itertools

import yaml

def debug(line):
    """Write debug line to standard error."""
    sys.stderr.write("---" + str(line) + "\n")

def read_update(stream):
    """Read update structure (ends on empty line)."""
    lines = []
    while 1:
        line = stream.readline()
        if not line:
            return
        if not line.strip():
            break
        lines.append(line)
    return yaml.load("".join(lines))

# Alternative Functional implementation of the imperative read_update() above.
#
# It uses some (obscure?) itertools functions, so it probably won't make any 
# sense unless you have some experience with the module. 
def read_update2(stream):
    """Read update structure (ends on empty line)."""
    def repeatfunc(func, *args):
        return itertools.starmap(func, itertools.repeat(args))
    yamldata = itertools.takewhile(str.strip, repeatfunc(stream.readline))
    if yamldata:
        return yaml.load("".join(yamldata))        

def send_command(update, command=None):
    """
    Send command for your robot.
    
    If this is the response of a update structure, pass the object. If you 
    are sending a command at the initilization process you won't
    have an update structure to reference, just set it to None.
     
    Note that you must send one and only one command per update loop. If you 
    don't have a command to send for a loop iteration, just send an empty string. 
    If you fail to send a command the events loop will hang.     
    """
    update_id = (update["id"] if update else "-")        
    sys.stdout.write("%s %s\n" % (update_id, command or ""))
    sys.stdout.flush()
        
def main(args, control):
    """Main function wrapper that can be be called from the bot script."""
    initfile, = args
    init = yaml.load(open(initfile).read())
    control(init, iter(lambda: read_update(sys.stdin), None))
