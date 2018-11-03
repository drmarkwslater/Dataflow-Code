# Parser routines for DFC Compiler


def label_check(in_str):
    """Check the given token doesn't have odd characters in it that we can't deal with"""
    #TODO
    return True


def process_bracketed_csv_list(in_toks):
    """Assume the set of toks is a bracketed group of comma-separate values"""
    if in_toks[0] != "(":
        raise SyntaxError("Expected '(' and got %s" % in_toks[0])

    out_toks = []
    idx = 1
    while idx < len(in_toks):

        # end of in_data list?
        if in_toks[idx] == ")":
            return out_toks, idx+1

        # add the CSV values
        out_toks.append(in_toks[idx])
        if in_toks[idx+1] == ",":
            idx += 1
        elif in_toks[idx+1] != ")":
            raise SyntaxError("Error in CSV list definition. Expect ',' or ')' and got '%s'" % in_toks[idx+1])

        idx += 1

    raise SyntaxError("Reached end of input while processing bracketed CSV list without finding ')'")


def preprocess_channel_links(in_toks):
    """Take the shlex'd tokens and stick ones together that are relevant"""
    if in_toks[0] != "{":
        raise SyntaxError("Expected '{' and got %s" % in_toks[0])

    out_toks = []
    idx = 1
    next_tok = ""
    in_num = False
    in_python = False
    while idx < len(in_toks):
        # end of in_toks list?
        if in_toks[idx] == "}":
            if next_tok == "":
                raise SyntaxError("Expected node after '->'")
            out_toks.append(next_tok)
            return out_toks, idx+1

        # check for '->' tokens
        if in_toks[idx] == '-' and in_toks[idx+1] == '>':
            out_toks.append(next_tok)
            next_tok = ""
            out_toks.append('->')
            idx += 2
            in_num = False
        elif in_toks[idx].isdigit() and not in_num:
            # Check for numeric constants
            out_toks.append(next_tok)
            next_tok = in_toks[idx]
            idx += 1
            in_num = True
        elif in_toks[idx] == '__python__' and not in_python:
            # check if we are in a python node
            if next_tok:
                out_toks.append(next_tok)
            next_tok = in_toks[idx]
            idx += 1
            in_python = True
        elif ':' in in_toks[idx-1:idx+2] or '<' in in_toks[idx-1:idx+1] or '>' in in_toks[idx:idx+2] or in_num\
                or in_python:
            # Toks to be added together
            next_tok += in_toks[idx]
            idx += 1
        else:
            # preserve the spaces
            if next_tok:
                out_toks.append(next_tok)
            next_tok = in_toks[idx]
            idx += 1

    raise SyntaxError("Reached end of channel link section without finding '}'")


def split_node_def_in(node_def):

    # split the input channel
    in_chan = node_def.split(':')[0]

    # now the name
    node_name = node_def.split(':')[1]
    node_label = ""
    if node_def.split(':')[1].find('<') > -1:
        # we have a label as well
        node_label = node_name[node_name.find('<') + 1:node_name.find('>')]
        node_name = node_def.split(':')[1].split('<')[0]

    return in_chan, node_name, node_label


def split_node_def_out(node_def):

    # split the output channel
    out_chan = node_def.split(':')[-1]

    # now the name
    node_name = node_def.split(':')[-2]
    node_label = ""
    if node_def.split(':')[-2].find('<') > -1:
        # we have a label as well
        node_label = node_name[node_name.find('<') + 1:node_name.find('>')]
        node_name = node_def.split(':')[-2].split('<')[0]

    return out_chan, node_name, node_label
