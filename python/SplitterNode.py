# Node to split a list of elements and process the given nodes with each one

from Node import Node
from Channel import Channel


class SplitterNode (Node):

    def __init__(self):
        # TODO: Protect against being set NotReady by upstream nodes while processing stuff
        # set the name
        self.name_ = "SplitterNode"
        self.label_ = ""

        # initial status
        self.status_ = Node.NotReady_

        # initial index of the splitter
        self.curr_index_ = 0

        # Provide an input and output data channel
        self.out_channels_ = [Channel("output", self)]
        self.in_channels_ = [Channel("input", self)]

    def process(self):
        """Split the data and push each part down the line"""

        # Are the inputs ready?
        for chan in self.in_channels_:
            if not chan.get_input_link() or not chan.get_input_link().is_parent_ready():
                return

        # split and send the current 'packet' down the chain
        for chan in self.out_channels_[0].output_links_:
            chan.parent_node_.set_not_ready()

        self.out_channels_[0].data_ = self.in_channels_[0].get_input_link().data_[self.curr_index_]
        self.status_ = Node.Ready_

    def next_packet(self):
        """Retrieve the next packet and set as not ready"""

        if self.curr_index_ >= len(self.in_channels_[0].get_input_link().data_) - 1:
            # Processed everything
            return False

        self.curr_index_ += 1
        self.status_ = Node.NotReady_
        return True
