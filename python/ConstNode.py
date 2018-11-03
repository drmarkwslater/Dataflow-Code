# String Constant Node Class definition

from Node import Node
from Channel import Channel


class ConstNode (Node):

    def __init__(self, const_value):
        # set the name
        self.name_ = "ConstNode"
        self.label_ = ""

        # initial status
        self.status_ = Node.NotReady_

        # Only relevant thing is the output data channel
        self.out_channels_ = [Channel("out", self)]
        self.in_channels_ = []

        # finally set the constant value to pass on
        if const_value[0] == '"' and const_value[-1] == '"':
            self.const_val_ = const_value.strip('"')
        else:
            try:
                # can we create an integer out of this?
                self.const_val_ = int(const_value)
            except ValueError:
                # no, so it must be a float
                self.const_val_ = float(const_value)

    def process(self):
        """Just push the data down the chain"""
        for chan in self.out_channels_[0].get_output_links():
            chan.parent_node_.set_not_ready()

        self.out_channels_[0].data_ = self.const_val_
        self.status_ = Node.Ready_
        return True


