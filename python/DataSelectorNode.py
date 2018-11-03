# String Constant Node Class definition

from Node import Node
from Channel import Channel


class DataSelectorNode (Node):

    def __init__(self):
        # set the name
        self.name_ = "DataSelectorNode"
        self.label_ = ""

        # initial status
        self.status_ = Node.NotReady_

        # Only relevant thing is the output data channel
        self.out_channels_ = [Channel("output", self)]
        self.in_channels_ = [Channel("input1", self), Channel("input2", self)]

    def process(self):
        """Go through all inputs and the first that is Ready, give that"""
        for chan in self.in_channels_:
            if chan.get_input_link() and chan.get_input_link().is_parent_ready():
                self.out_channels_[0].data_ = chan.get_input_link().data_
                self.status_ = Node.Ready_
                return
