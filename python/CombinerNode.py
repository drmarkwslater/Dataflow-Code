# Node that pairs with a Splitter Node to combine the results of the split

from Node import Node
from Channel import Channel


class CombinerNode (Node):

    def __init__(self):
        # set the name
        self.name_ = "CombinerNode"
        self.label_ = ""

        # initial status
        self.status_ = Node.NotReady_

        # buffer
        self.buffer_ = None

        # Provide an input and output data channel
        self.out_channels_ = [Channel("output", self)]
        self.in_channels_ = [Channel("input", self)]

        # Linked splitter node
        self.sp_node_ = None

    def link_nodes(self, node_list):
        """link the splitter node"""
        for nd in node_list:
            if nd.name_ == "SplitterNode":
                self.sp_node_ = nd

    def process(self):
        """process the given input and store it in the buffer until all have been completed"""

        # Are the inputs ready?
        for chan in self.in_channels_:
            if not chan.get_input_link() or not chan.get_input_link().is_parent_ready():
                return

        # Take that input and store it
        if not self.buffer_:
            self.buffer_ = self.in_channels_[0].get_input_link().data_
        else:
            self.buffer_ += self.in_channels_[0].get_input_link().data_

        # Poke the Splitter to send the next 'packet'
        if not self.sp_node_.next_packet():
            self.out_channels_[0].data_ = self.buffer_
            self.status_ = Node.Ready_
