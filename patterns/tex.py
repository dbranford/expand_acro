import pyparsing as pp


def environment(name):
    patt_begin = r"\begin{" + name + r"}"
    patt_end = r"\end{" + name + r"}"
    patt_env = pp.nested_expr(patt_begin, patt_end, ignore_expr=(grp | cmnt))
    return patt_env


def usepkg(name):
    patt_pkg = (r"\usepackage" + pp.Opt(opt) + grp).ignore(cmnt)
    return patt_pkg


def reqpkg(name):
    patt_pkg = (r"\RequirePackage" + pp.Opt(opt) + grp).ignore(cmnt)
    return patt_pkg


cmnt = pp.Literal(r"%") + pp.rest_of_line
cmnt.ignore(r"\%")

grp = pp.original_text_for(
    pp.nested_expr(
        r"{",
        r"}",
        ignore_expr=(pp.Literal(r"\{") | pp.Literal(r"\}") | cmnt),
    )
)

opt = pp.original_text_for(
    pp.nested_expr(
        "[",
        "]",
        ignore_expr=(pp.Literal(r"\[") | pp.Literal(r"\]") | grp | cmnt),
    )
)


documentclass = (
    r"\documentclass"
    + pp.Suppress(pp.ZeroOrMore(cmnt))
    + pp.Opt(opt)
    + pp.Suppress(pp.ZeroOrMore(cmnt))
    + pp.nested_expr("{", "}", ignore_expr=cmnt)
)

document = (
    pp.original_text_for(... + documentclass)("class")
    + ...
    + pp.original_text_for(environment("document"))("document")
).parse_with_tabs()


input = (pp.Literal(r"\include") ^ pp.Literal(r"\input")) + pp.nested_expr("{", "}")(
    "fname"
)

star = pp.Literal(r"*")


def generic_macro(macro):
    pattern = pp.original_text_for("\\" + macro + pp.ZeroOrMore(star ^ grp ^ opt))
    return pattern


def macro_n(
    args=1,
    name=pp.Word(pp.alphas),
    options=0,
    star=0,
):
    """Produces a pattern to match a macro with <star> *, followed by <options> [] arguments, and <args> {} arguments"""
    pattern = pp.Literal("\\") + name + pp.Literal("*")[star] + opt[options]
    pattern = pattern + grp[(args)].set_results_name("args", list_all_matches=True)
    pattern.ignore(cmnt)
    return pattern


def macro(
    args=[grp],
    name=pp.Word(pp.alphas),
    options=0,
    star=0,
):
    """Produces a pattern to match a macro with <star> *, followed by <options> [] arguments, and N args as set in the tuple passed to args (these can inlude star, [], etc)"""
    pattern = pp.Literal("\\") + name + pp.Literal("*")[star] + opt[options]
    for arg in args:
        pattern = pattern + arg
    pattern.ignore(cmnt)
    return pattern
