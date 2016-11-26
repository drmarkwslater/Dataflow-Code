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
        else:
            next_tok += in_toks[idx]
            idx += 1

    raise SyntaxError("Reached end of channel link section without finding '}'")