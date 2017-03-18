# String Constant Node Class definition

from Node import Node
from Channel import OutputChannel


class StringConstNode (Node):

    def __init__(self, const_value):
        # set the name
        self.name_ = "StringConstNode"
        self.label_ = ""

        # initial status
        self.status_ = Node.NotReady_

        # Only relevant thing is the output data channel
        self.out_channels_ = [OutputChannel("out", self)]
        self.in_channels_ = []

        # finally set the constant value to pass on
        self.const_str_ = const_value

    def process(self):
        """Just push the data down the chain"""
        for chan in self.out_channels_[0].output_links_:
            chan.parent_node_.set_not_ready()

        self.out_channels_[0].data_ = self.const_str_
        self.status_ = Node.Ready_


