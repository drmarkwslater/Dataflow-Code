#!/bin/python

import shlex
import sys
import os

# Add the python directory to the sys path
sys.path.append(os.path.join(os.path.dirname(__file__), '../python'))

from dfc_parser import label_check, process_bracketed_csv_list, preprocess_channel_links
from Runtime import getRuntime
from Node import Node
from PythonNode import PythonNode


print "---------------------------------------------------"
print "Compiling..."
print "---------------------------------------------------\n"
toks = shlex.shlex(open("examples/HelloWorld.dfc").read())

# Set up the runtime
curr_runtime = getRuntime()

# Go over the toks and create any nodes
toks_list = list(toks)
idx = 0
while idx < len(toks_list):

    tok = toks_list[idx]

    # Check for node definition
    if tok == "node":

        # Definition of node as follows:
        # node NAME (in1, in2 ...) (out1, out2 ...) { LINKS }

        # Name first
        name = toks_list[idx+1]
        if not label_check(name):
            print "[error] Problem with name of node '%s'" % name
            break

        idx += 2

        # list of input channels
        try:
            in_data_chans, new_idx = process_bracketed_csv_list(toks_list[idx:])
        except SyntaxError as err:
            print "[error] Syntax error in input data channel definition for node '%s': %s" % (err, name)
            break

        idx += new_idx

        # list of output channels
        try:
            out_data_chans, new_idx = process_bracketed_csv_list(toks_list[idx:])
        except SyntaxError as err:
            print "[error] Syntax error in output data channel definition for node '%s': %s" % (err, name)
            break

        idx += new_idx

        # if not, process the channel links
        try:
            link_toks, new_idx = preprocess_channel_links(toks_list[idx:])
        except SyntaxError as err:
            print "[error] Syntax error in channel link definition for node '%s': %s" % (err, name)
            break

        idx += new_idx

        # Create the given node and add to runtime
        nd = None
        if link_toks[0][:10] == "__python__":
            # pure python node
            nd = PythonNode(name, in_data_chans, out_data_chans, link_toks[0])
        else:
            nd = Node(name, in_data_chans, out_data_chans, link_toks)

        curr_runtime.add_node(nd)


# Now set the Runtime going
print "\n\n\n---------------------------------------------------"
print "Executing Runtime..."
print "---------------------------------------------------\n"

curr_runtime.execute()