# Node Class definition

import copy

from dfc_parser import split_node_def_in, split_node_def_out
from Runtime import getRuntime
from Channel import Channel


def create_special_node(node_def):
    """Check if we can create a 'special' node from this def"""
    from ConstNode import ConstNode
    nd = None
    if node_def[0] == '"' and node_def[-1] == '"':
        # String constant node
        nd = ConstNode(node_def)
    else:
        try:
            # can we create a number out of this?
            val = float(node_def)
            nd = ConstNode(node_def)
        except ValueError:
            pass

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
        self.progress_ = False

        print "[node] Creating Node '%s'..." % name

        # initial status
        self.status_ = Node.NotReady_

        # Process the exposed input/output channels
        self.in_channels_ = []
        self.out_channels_ = []
        for chan in in_data_chans:
            self.in_channels_.append(Channel(chan, self))
        for chan in out_data_chans:
            self.out_channels_.append(Channel(chan, self))

        # now go through and create all the links and referenced nodes
        # General form of:  node_type<label>:out_chan -> in_chan:node_type<label>:...
        self.nodes_ = []
        for idx in range(0, len(link_toks)):

            if link_toks[idx] == "->":
                # We have a link so process the input and output defs and create the nodes if required
                out_nd, out_chan_name = self.parse_def_and_create_node(link_toks[idx-1], out_node=True)
                in_nd, in_chan_name = self.parse_def_and_create_node(link_toks[idx+1], out_node=False)

                # Find the in/out channel
                if out_nd == self:
                    # this is the input channel for the container node
                    out_chan = out_nd.find_in_channel(out_chan_name)
                else:
                    out_chan = out_nd.find_out_channel(out_chan_name)

                if in_nd == self:
                    # this is the output channel for the container node
                    in_chan = in_nd.find_out_channel(in_chan_name)
                else:
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

    def link_nodes(self, nd_links):
        """Set any links up between nodes (e.g. Combiner -> Splitter)"""
        pass

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
                for nd in self.nodes_:
                    if nd.label_ == node_label and nd.name_ == node_name:
                        print "[node] Using node '%s<%s>' with output channel '%s' in node def '%s'" % \
                              (nd.name_, nd.label_, nd_chan, self.name_)
                        return nd, nd_chan

                print "[node] Creating node, type '%s', with label '%s' in node def '%s'" % (node_name, node_label, self.name_)

            elif out_node and len(node_def.split(':')) == 3:
                # we have a chained node def so we must have already created this output node
                nd = self.nodes_[-1]
                return nd, nd_chan
            else:
                print "[node] Creating node of type '%s' in node def '%s'" % (node_name, self.name_)

            # if not create a new one of this type and add to the node list
            # Check the runtime for this node
            tmp_nd = getRuntime().find_node_by_name(node_name)

            if not tmp_nd:
                raise SyntaxError("[node] Unable to find node '%s' in Runtime for node def '%s'" %
                                  (node_name, self.name_))
            # Copy it
            nd = copy.deepcopy(tmp_nd)

            # if any labels are the same, link them
            nd_links = []
            for nd2 in self.nodes_:
                if nd2.label_ == node_label:
                    nd_links.append(nd2)
            nd.link_nodes(nd_links)

            # set the label
            nd.label_ = node_label

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

    def is_ready(self, chan_name = ""):
        """Return if the node is ready or not"""
        return self.status_ == Node.Ready_

    def set_not_ready(self):
        """set this node as not ready"""
        self.status_ = Node.NotReady_

    def process(self):
        """Attempt to process this node. Just go over the contained nodes and attempt to process non-ready ones"""
    
        # Check if all inputs are ready
        for chan in self.in_channels_:
            if not chan.get_input_link().is_parent_ready():
                return
        
        # Loop over all the nodes
        set_ready = True
        self.progress_ = False
        for nd in self.nodes_:

            # If the node is Ready, just move on
            if nd.is_ready():
                continue

            # It's not ready, so attempt to process
            set_ready = False
            nd.process()
            if (hasattr(nd, "progress_") and nd.progress_) or nd.is_ready():
                self.progress_ = True

        # if all nodes have been processed, set ourselves ready
        if set_ready:
            self.status_ = Node.Ready_
