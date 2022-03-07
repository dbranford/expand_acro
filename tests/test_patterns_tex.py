import aexpand.patterns as patt


def test_comment1():
    pattern = patt.tex.cmnt.search_string(r"Foo \% Bar % Bat")
    assert pattern.as_list() == [["%", " Bat"]]


def test_comment2():
    pattern = patt.tex.cmnt.search_string(r"Foo % Bar \% Bat")
    assert pattern.as_list() == [["%", " Bar \\% Bat"]]


def test_comment3():
    pattern = patt.tex.cmnt.search_string('Foo \\% Bar % Bat \n Baz "%" Foobar')
    assert pattern.as_list() == [["%", " Bat "], ["%", '" Foobar']]


def test_group1():
    pattern = patt.tex.grp.search_string(r"Foo {Baz}")
    assert pattern.as_list() == [["{Baz}"]]


def test_group2():
    pattern = patt.tex.grp.search_string("{Foo%bar}\nbat}")
    assert pattern.as_list() == [["{Foo%bar}\nbat}"]]


def test_group3():
    pattern = patt.tex.grp.search_string(r"Foo {Bar {Bat}} {Baz \{Foobar\}}")
    assert pattern.as_list() == [["{Bar {Bat}}"], [r"{Baz \{Foobar\}}"]]


def test_opt1():
    pattern = patt.tex.opt.search_string(r"foo [bar]")
    assert pattern.as_list() == [[r"[bar]"]]


def test_opt2():
    pattern = patt.tex.opt.search_string(r"foo [bar={]}]")
    assert pattern.as_list() == [[r"[bar={]}]"]]


def test_class1():
    pattern = patt.tex.documentclass.parse_string(
        r"\documentclass[aps,sort&compress,12={foo}]{revtex4-2}"
    )
    assert pattern.as_list() == [
        r"\documentclass",
        r"[aps,sort&compress,12={foo}]",
        ["revtex4-2"],
    ]


def test_class2():
    pattern = patt.tex.documentclass.parse_string(
        "\\documentclass%\n[\na4paper,% make a4 paper\n11pt,%\n]\n{article}"
    )
    assert pattern.as_list() == [
        "\\documentclass",
        "[\na4paper,% make a4 paper\n11pt,%\n]",
        ["article"],
    ]


def test_doc1():
    doc = "\n".join(
        [
            r"%arara: pdflatex",
            r"\documentclass[a4paper]{article}",
            r"\usepackage{acro}",
            r"\usepackage{hyperref}",
            "",
            r"\begin{document}",
            "Foo",
            r"\end{document}",
        ]
    )
    matched = patt.tex.document.parse_string(doc)
    assert matched.as_list() == [
        r"%arara: pdflatex" + "\n" + r"\documentclass[a4paper]{article}",
        "\n".join([r"\usepackage{acro}", r"\usepackage{hyperref}"]),
        "\n".join([r"\begin{document}", "Foo", r"\end{document}"]),
    ]


def test_doc2():
    matched = patt.tex.document.parse_string(
        "\n".join(
            [
                r"%arara: pdflatex",
                r"\documentclass%",
                r"[a4paper]%",
                r"{%",
                r"article%",
                r"}",
                r"\usepackage{acro} % Acro package",
                r"\usepackage{hyperref}",
                r"%Preamble finished",
                "",
                r"\begin{document}% Now write text",
                "Foo",
                "%Bar",
                "Foobar %Not Foobat",
                r"\end{document}",
            ]
        )
    )
    assert matched.as_list() == [
        "\n".join(
            [
                r"%arara: pdflatex",
                r"\documentclass%",
                r"[a4paper]%",
                r"{%",
                r"article%",
                r"}",
            ]
        ),
        "\n".join(
            [
                r"\usepackage{acro} % Acro package",
                r"\usepackage{hyperref}",
                r"%Preamble finished",
            ]
        ),
        "\n".join(
            [
                r"\begin{document}% Now write text",
                "Foo",
                "%Bar",
                "Foobar %Not Foobat",
                r"\end{document}",
            ]
        ),
    ]
