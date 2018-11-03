# Python Node Class definition

from Node import Node


class PythonNode (Node):

    def __init__(self, name, in_data_chans, out_data_chans, python_code):

        # call base class setup with empty link toks
        Node.__init__(self, name, in_data_chans, out_data_chans, "")

        # check the code is included correctly: __python__("...")
        if python_code.split('"')[0] != "__python__(":
            raise SyntaxError("PythonNode expects __python__ in node definition")

        if python_code.split('"')[-1] != ")":
            raise SyntaxError("Couldn't find closing bracket in PythonNode definition")

        # store the code
        self.code_ = python_code[12:-2].strip()

    def process(self):
        """Run the python code with the attached inputs"""
        # Are the inputs ready?
        # TODO: Should be member of Node
        for chan in self.in_channels_:
            if not chan.get_input_link() or not chan.get_input_link().is_parent_ready():
                return

        # Add the variable defs to the start of the code block
        tmp_code = ""
        for chan in self.out_channels_:
            tmp_code += """%s = None
""" % chan.name_

        for chan in self.in_channels_:
            # TODO: Can probably just use %r here for __repr__
            if type(chan.get_input_link().data_) == float:
                tmp_code += """%s = %f
""" % (chan.name_, chan.get_input_link().data_)
            elif type(chan.get_input_link().data_) == int:
                tmp_code += """%s = %d
""" % (chan.name_, chan.get_input_link().data_)
            elif type(chan.get_input_link().data_) == list:
                tmp_code += """%s = %s
""" % (chan.name_, chan.get_input_link().data_)
            elif type(chan.get_input_link().data_) == bool:
                tmp_code += """%s = %r
""" % (chan.name_, chan.get_input_link().data_)
            else:
                tmp_code += """%s = "%s"
""" % (chan.name_, chan.get_input_link().data_.replace('\n', '\\n'))

        # Add the code for the output variables
        tmp_code2 = "\n"
        for chan_idx in range(0, len(self.out_channels_)):
            tmp_code2 += """self.out_channels_[%d].data_ = %s
""" % (chan_idx, self.out_channels_[chan_idx].name_)

        # run the code - hack for getting stdin working within exec
        exec(tmp_code + self.code_ + tmp_code2)

        for out_chan in self.out_channels_:
            for chan in out_chan.output_links_:
                chan.parent_node_.set_not_ready()

        self.status_ = Node.Ready_
