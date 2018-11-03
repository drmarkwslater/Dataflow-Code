# Data channel classes


class Channel:

    def __init__(self, name, parent):
        self.name_ = name
        self.parent_node_ = parent
        self.output_links_ = []
        self.data_ = None
        self.input_link_ = None

    def add_output_link(self, chan):
        """Add the given channel to the list of downstream outputs"""
        self.output_links_.append(chan)

    def set_input_link(self, chan):
        """Set the output channel that links to this input channel"""
        self.input_link_ = chan

    def get_output_links(self):
        """Return the list of input channels that link to this output channel.
        If the output_links_ (in theory, an input channel) has output_links itself,
        then then combine them and return that"""
        tmp_chan = []
        for c in self.output_links_:
            tmp_chan += c.get_output_links()

        return tmp_chan

    def get_input_link(self):
        """Return the output channel that links to this input channel.
        If the input_link_ (in theory, an output channel) has input_link itself,
        then return this as this is a pass through link out of the container node.
        This can be several layers deep so keep going backwards until we find a non-input linked channel"""
        curr_chan = self
        while curr_chan.input_link_:
            if curr_chan.input_link_.input_link_:
                curr_chan = curr_chan.input_link_
            else:
                break
        return curr_chan.input_link_

    def is_parent_ready(self):
        """Check if the parent of this channel is ready. Note that this gives the
        node the option of deciding if it's ready based on the channel
        that is requesting the information"""

        return self.parent_node_.is_ready(self.name_)