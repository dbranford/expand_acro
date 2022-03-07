import aexpand.patterns as patt


def test_ac_printable1():
    matched = patt.acro.ac_printable().parse_string(r"\ac{foo}")
    assert matched.as_list() == [r"\ac{foo}"]


def test_ac_printable2():
    matched = patt.acro.ac_printable().search_string(
        "Blah, blah\n" + r"\ac{foo} % An acronym" + "\n" + r"This is \Acp{bar}"
    )
    assert matched.as_list() == [[r"\ac{foo}"], [r"\Acp{bar}"]]


def test_ac_printable3():
    matched = patt.acro.ac_printable(ac_ids=["foo"]).search_string(
        "Blah, blah\n" + r"\ac{foo} % An acronym" + "\n" + r"This is \Acp{bar}"
    )
    assert matched.as_list() == [[r"\ac{foo}"]]


def test_ac_noprintable1():
    matched = patt.acro.ac_noprintable().search_string(r"\acresetall \acuse{foo}")
    assert matched.as_list() == [[r"\acresetall"], [r"\acuse{foo}"]]


def test_ac_noprintable2():
    matched = patt.acro.ac_noprintable(ac_ids=["foo"]).search_string(
        r"\acresetall \acuse{foo} \acuse{bar}"
    )
    assert matched.as_list() == [[r"\acresetall"], [r"\acuse{foo}"]]
