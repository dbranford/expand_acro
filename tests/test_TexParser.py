from aexpand.document import Document
from aexpand.parser import TexParser

from pathlib import Path

FULL_DIR = Path(__file__).parent / "full"

doc1_class = r"% Foo" + "\n" + r"\documentclass[a4paper]{article}"
doc1_preamble = "\n".join(
    [
        r"\usepackage{acro}",
        r"\usepackage{hyperref}",
        "",
        r"\DeclareAcronym{ac1}{",
        "\tshort = short1,",
        "\tlong = long1 very long,",
        "}",
        r"\DeclareAcronym{ac2}{",
        "\tshort = short2,",
        "\tlong = long2,",
        "}",
    ]
)
doc1_body = "\n".join(
    [
        r"\begin{document}",
        r"\ac{ac1}",
        r"\Ac{ac1}",
        r"\ac{ac1}",
        "Foo",
        r"\end{document}",
    ]
)
doc2_class = "\n".join(
    [
        r"%arara: pdflatex",
        r"\documentclass%",
        r"[a4paper]%",
        r"{%",
        r"article%",
        r"}",
    ]
)
doc2_preamble = "\n".join(
    [
        r"\usepackage{acro} % Acro package",
        r"\DeclareAcronym{CD}{",
        "\tshort = CD,",
        "\tlong = compact disc,",
        r"}",
        r"\usepackage{hyperref}",
        r"%Preamble finished",
    ]
)
doc2_body = "\n".join(
    [
        r"\begin{document}% Now write text",
        r"Foo \ac{CD}",
        r"%Bar,",
        r"Foobar %Not Foobat",
        r"\end{document}",
    ]
)

with open(FULL_DIR / "test1.tex") as file:
    doc1 = file.read()

with open(FULL_DIR / "test2.tex") as file:
    doc2 = file.read()

parser = TexParser()


def test_input_string1():
    document = parser.input_string(doc1)
    assert type(document) == Document
    assert document.docclass == doc1_class
    assert document.preamble == doc1_preamble
    assert document.body == doc1_body


def test_input_string2():
    document = parser.input_string(doc2)
    assert type(document) == Document
    assert document.docclass == doc2_class
    assert document.preamble == doc2_preamble
    assert document.body == doc2_body


def test_input_file1():
    document = parser.input_file(FULL_DIR / "test1.tex")
    assert type(document) == Document
    assert document.docclass == doc1_class
    assert document.preamble == doc1_preamble
    assert document.body == doc1_body


def test_input_file2():
    document = parser.input_file(FULL_DIR / "test2.tex")
    assert type(document) == Document
    assert document.docclass == doc2_class
    assert document.preamble == doc2_preamble
    assert document.body == doc2_body
