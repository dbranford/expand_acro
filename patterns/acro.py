import pyparsing as pp
import expand_acro.patterns.tex as tex

acsetup = pp.Suppress(pp.Literal(r"\acsetup")) + tex.grp

ac_id = pp.Word(pp.alphanums)

ac_keys = pp.Word(pp.alphas)

ac_vals = pp.original_text_for(
    pp.OneOrMore(pp.nested_expr("{", "}") ^ pp.OneOrMore(pp.CharsNotIn(",")))
)
ac_keyvals = pp.delimited_list(
    pp.Group(ac_keys + pp.Opt(pp.Suppress("=") + pp.OneOrMore(ac_vals))),
    delim=",",
)

DeclareAcronym = pp.original_text_for(
    r"\DeclareAcronym{" + ac_id("id") + r"}" + tex.grp("contents"),
    as_string=False,
)


use_macros = ["ac", "aca", "acf", "acl", "acs"]
use_macros += ["i" + ac for ac in use_macros] + [ac + "p" for ac in use_macros]
use_macros += [ac[0].upper() + ac[1:] for ac in use_macros]
use_macros += [ac + "*" for ac in use_macros]
# When do these accpet an optional argument?


def ac_macros(macros=use_macros, ids=ac_id):
    pattern = pp.original_text_for(
        tex.macro(
            args=["{" + pp.Or(ids)("id") + "}"],
            name=pp.Or(macros)("macro"),
        ),
        as_string=False,
    )
    return pattern


def ac_printable(macros=use_macros, ac_ids=None):
    # Every \ac{} variant
    if ac_ids is None:
        pattern = ac_macros(macros=use_macros)
    else:
        pattern = ac_macros(macros=use_macros, ids=ac_ids)
    return pp.original_text_for(pattern)


def ac_noprintable(ac_ids=ac_id):
    # Zero arguments
    noprint_macros = pp.Or(["acresetall", "acuseall"])
    pattern = pp.original_text_for(tex.macro(args=[], name=noprint_macros))
    # One argument, can take id
    noprint_macros = ["acreset", "acuse"]
    if ac_ids is None:
        pattern = pattern | ac_macros(macros=noprint_macros)
    else:
        pattern = pattern | ac_macros(macros=noprint_macros, ids=ac_ids)
    # One argument, doesn't take id
    pattern = pattern | tex.macro("acsetup")
    return pp.original_text_for(pattern)


def ac_weird(ac_ids=ac_id):
    # pattern = tex.macro_n(0, name="printbibliography", options=1)
    return pp.NoMatch()


def ac_aux(ac_ids=ac_id):
    return pp.NoMatch()
