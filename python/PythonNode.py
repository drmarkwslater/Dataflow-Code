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
            if not chan.input_link_ or not chan.input_link_.parent_node_.is_ready():
                return

        # Add the variable defs to the start of the code block
        tmp_code = ""
        for chan in self.in_channels_:
            if type(chan.input_link_.data_) == float or type(chan.input_link_.data_) == int:
                tmp_code += """%s = %d
""" % (chan.name_, chan.input_link_.data_)
            else:
                tmp_code += """%s = '%s'
""" % (chan.name_, chan.input_link_.data_)

        # run the code
        exec(tmp_code + self.code_)
        self.status_ = Node.Ready_
