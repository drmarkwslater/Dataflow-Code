# Node Class definition

import copy

from dfc_parser import split_node_def_in, split_node_def_out
from Runtime import getRuntime
from Channel import OutputChannel, InputChannel


def create_special_node(node_def):
    """Check if we can create a 'special' node from this def"""
    nd = None
    if node_def[0] == '"' and node_def[-1] == '"':
        # String constant node
        from StringConstNode import StringConstNode
        nd = StringConstNode(node_def.strip('"'))

    return nd


def set_channel_link(out_nd, out_chan_name, in_nd, in_chan_name):
    """Set up the channel link between these nodes"""

    # Find the out channel
    out_chan = out_nd.find_out_channel(out_chan_name)
    in_chan = in_nd.find_in_channel(in_chan_name)

    # are these valid channels?
    if not out_chan:
        raise SyntaxError("[node] Error: Couldn't find output channel '%s' in node '%s'" %
                          (out_chan_name, out_nd.name_))

    if not in_chan:
        raise SyntaxError("[node] Error: Couldn't find input channel '%s' in node '%s'" %
                          (in_chan_name, in_nd.name_))

    out_chan.add_output_link(in_chan)
    in_chan.set_input_link(out_chan)


class Node:

    NotReady_ = 0
    Ready_ = 1

    def __init__(self, name, in_data_chans, out_data_chans, link_toks, label=""):

        # set the name and label
        self.name_ = name
        self.label_ = label

        print "[node] Creating Node '%s'..." % name

        # initial status
        self.status_ = Node.NotReady_

        # Process the exposed input/output channels
        self.in_channels_ = []
        self.out_channels_ = []
        for chan in in_data_chans:
            self.in_channels_.append(InputChannel(chan, self))
        for chan in out_data_chans:
            self.out_channels_.append(OutputChannel(chan, self))

        # now go through and create all the links and referenced nodes
        # General form of:  node_type<label>:out_chan -> in_chan:node_type<label>:...
        self.nodes_ = []
        for idx in range(0, len(link_toks)):

            if link_toks[idx] == "->":
                # We have a link so process the input and output defs and create the nodes if required
                out_nd, out_nd_chan = self.parse_def_and_create_node(link_toks[idx-1], out_node=True)
                in_nd, in_nd_chan = self.parse_def_and_create_node(link_toks[idx+1], out_node=False)

                # Set the channel link - special case for self input/output channels
                # TODO: Straight pass through node will not work
                if out_nd is self:
                    self.find_in_channel(out_nd_chan).set_pass_through(in_nd.find_in_channel(in_nd_chan))
                elif in_nd is self:
                    self.find_out_channel(in_nd_chan).set_pass_through(out_nd.find_out_channel(out_nd_chan))
                else:
                    set_channel_link(out_nd, out_nd_chan, in_nd, in_nd_chan)

    def parse_def_and_create_node(self, node_def, out_node=True):
        """Go over the given string and return the appropriate created node"""

        nd = create_special_node(node_def)
        if nd:
            nd_chan = nd.out_channels_[0].name_
            self.nodes_.append(nd)
        elif len(node_def.split(':')) == 1:
            # This is actually the input or output channel of this node
            nd = self
            nd_chan = node_def
        else:
            # general node def
            if out_node:
                nd_chan, node_name, node_label = split_node_def_out(node_def)
            else:
                nd_chan, node_name, node_label = split_node_def_in(node_def)

            # Check for any previously labelled node
            if node_label:
                node_found = False
                for nd in self.nodes_:
                    if nd.label_ == node_label:
                        print "[node] Using node '%s<%s>' with output channel '%s' to node '%s'" % \
                              (nd.name_, nd.label_, nd_chan, self.name_)
                        return nd, nd_chan

                print "[node] Creating node with label '%s' in node def '%s'" % (node_label, self.name_)

            elif out_node and node_def.split(':') == 3:
                # we have a chained node def so we must have already created this output node
                nd = self.nodes_[-1]
                return nd, nd_chan

            # if not create a new one of this type and add to the node list
            # Check the runtime for this node
            tmp_nd = getRuntime().find_node_by_name(node_name)

            if not tmp_nd:
                raise SyntaxError("[node] Unable to find node '%s' in Runtime for node def '%s'" %
                                  (node_name, self.name_))
            # Copy it
            nd = copy.deepcopy(tmp_nd)
            nd.label = node_label

            # append to the list
            self.nodes_.append(nd)

        return nd, nd_chan

    def find_out_channel(self, chan_name):
        """Return the output channel as found by name"""
        for chan in self.out_channels_:
            if chan.name_ == chan_name:
                return chan

        return None

    def find_in_channel(self, chan_name):
        """Return the input channel as found by name"""
        for chan in self.in_channels_:
            if chan.name_ == chan_name:
                return chan

        return None

    def is_ready(self):
        """Return if the node is ready or not"""
        return self.status_ == Node.Ready_

    def set_not_ready(self):
        """set this node as not readyt"""
        self.status_ = Node.NotReady_

    def process(self):
        """Attempt to process this node. Just go over the contained nodes and attempt to process non-ready ones"""
        # Check if all inputs are ready
        for chan in self.in_channels_:
            if not chan.input_link_.parent_node_.is_ready():
                return

        # Loop over all the nodes
        set_ready = True
        for nd in self.nodes_:

            # If the node is Ready, just move on
            if nd.is_ready():
                continue

            # It's not ready, so attempt to process
            set_ready = False
            nd.process()

        # if all nodes have been processed, set ourselves ready
        if set_ready:
            self.status_ = Node.Ready_
