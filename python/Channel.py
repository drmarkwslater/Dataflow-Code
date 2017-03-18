# Data channel classes


class Channel:

    def __init__(self, name, parent):
        self.name_ = name
        self.pass_chan_ = None
        self.parent_node_ = parent

    def set_pass_through(self, chan):
        """Make this channel a pass through (input or output) to the given channel"""
        self.pass_chan_ = chan


class OutputChannel(Channel):

    def __init__(self, name, parent):
        Channel.__init__(self, name, parent)
        self.output_links_ = []
        self.data_ = None

    def add_output_link(self, chan):
        """Add the given channel to the list of downstream outputs"""
        self.output_links_.append(chan)


class InputChannel(Channel):

    def __init__(self, name, parent):
        Channel.__init__(self, name, parent)
        self.input_link_ = None

    def set_input_link(self, chan):
        """Set the output channel that links to this input channel"""
        self.input_link_ = chan
