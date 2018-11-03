# Node to split a list of elements and process the given nodes with each one

from Node import Node
from Channel import Channel


class OutputCondNode (Node):

    def __init__(self):
        # TODO: Protect against being set NotReady by upstream nodes while processing stuff
        # set the name
        self.name_ = "OutputCondNode"
        self.label_ = ""
        self.cond_result_ = None
        self.cond_data_ = None

        # initial status
        self.status_ = Node.NotReady_

        # Provide the input data channel, input test channel and the two outputs
        self.in_channels_ = [Channel("input", self), Channel("test", self)]
        self.out_channels_ = [Channel("false_out", self), Channel("true_out", self)]

    def process(self):
        """Check the both inputs are ready so we can decide what output is ready"""

        # Are the inputs ready?
        for chan in self.in_channels_:
            if not chan.get_input_link() or not chan.get_input_link().is_parent_ready():
                return

        self.cond_result_ = bool(self.in_channels_[1].get_input_link().data_)
        if self.cond_result_:
            self.out_channels_[1].data_ = self.in_channels_[0].get_input_link().data_
        else:
            self.out_channels_[0].data_ = self.in_channels_[0].get_input_link().data_

        for out_chan in self.out_channels_:
            for chan in out_chan.output_links_:
                chan.parent_node_.set_not_ready()

        self.status_ = Node.Ready_

    def is_ready(self, chan_name = ""):
        """Return if the node is ready or not depending on channel that calls"""
        if self.status_ == Node.NotReady_:
            return False

        if not chan_name:
            return True
        elif chan_name == 'true_out' and self.cond_result_:
            return True
        elif chan_name == 'false_out' and not self.cond_result_:
            return True

        return False
