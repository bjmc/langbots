#!/usr/bin/python
import sys

# Third-party modules
import yaml

# App modules
from langbots import lib
from langbots import battlefield

def get_output_callback(field, filename):
    outputfd = open(filename, "w")
    def _wrapper(field):
        return write_state(field, outputfd)
    return _wrapper

def write_state(field, stream=sys.stdout):
    yamldata = yaml.dump(field, default_flow_style=False)
    stream.write(yamldata.strip() + "\n\n")
