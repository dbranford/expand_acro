import pyparsing as pp
import expand_acro.patterns as patt


def expand_group(text):
    return text[1:-1]


def strip_comments(text, patt_comment=patt.tex.cmnt):
    patt_comment = pp.Suppress(patt_comment)
    stripped = patt_comment.transform_string(text)
    return stripped
