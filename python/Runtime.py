# The runtime environment
def getRuntime():
    """return the current runtime or create it if it's not there"""
    if not getRuntime.curr_runtime_:
        getRuntime.curr_runtime_ = Runtime()

    return getRuntime.curr_runtime_
getRuntime.curr_runtime_ = None


class Runtime:

    def __init__(self):
        self.node_list_ = []

        # Add some system nodes in
        from SplitterNode import SplitterNode
        self.add_node(SplitterNode())

        from CombinerNode import CombinerNode
        self.add_node(CombinerNode())

        from OutputCondNode import OutputCondNode
        self.add_node(OutputCondNode())

        from DataSelectorNode import DataSelectorNode
        self.add_node(DataSelectorNode())

        #from InputCondNode import InputCondNode
        #self.add_node(InputCondNode())

    def add_node(self, node):
        """Add a node to the current runtime"""
        self.node_list_.append(node)
        print "Added Node '%s' to the Runtime" % node.name_

    def find_node_by_name(self, node):
        """
        Try to find the node of this name in the runtime
        :param node: node to find
        :return: The node object if found
        """

        for nd in self.node_list_:
            if nd.name_ == node:
                return nd

        return None

    def execute(self):
        """
        Execute the currently loaded nodes until everything is marked as 'Ready'
        """

        term_flag = False

        # Loop until term_flag set
        while not term_flag:

            term_flag = True

            # Loop over all the nodes
            for nd in self.node_list_:

                # If the node is Ready, or has unconnected inputs
                if nd.is_ready() or len(nd.in_channels_) > 0:
                    continue

                # It's not ready, so attempt to process and if we've made progress, keep going
                nd.process()

                if nd.progress_:
                    term_flag = False

