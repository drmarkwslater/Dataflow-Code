#!/bin/python

import shlex
import sys
import os

# Add the python directory to the sys path
sys.path.append(os.path.join(os.path.dirname(__file__), '../python'))

from dfc_parser import label_check, process_bracketed_csv_list, preprocess_channel_links

toks = shlex.shlex(open("examples/HelloWorld.dfc").read())

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

        # now process the channel links
        try:
            link_toks, new_idx = preprocess_channel_links(toks_list[idx:])
        except SyntaxError as err:
            print "[error] Syntax error in channel link definition for node '%s': %s" % (err, name)
            break

        print link_toks
        idx += new_idx
        print toks_list[idx:]
        break