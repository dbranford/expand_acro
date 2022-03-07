from expand_acro.expand_acro import expand
from pathlib import Path

FULL_DIR = Path(__file__).parent / "full"


def test_full1():
    test = expand(FULL_DIR / "test1.tex")
    with open(FULL_DIR / "soln1.tex") as file:
        soln = file.read()
        soln = soln[:-1]
    assert test == soln


def test_full2():
    test = expand(FULL_DIR / "test2.tex")
    with open(FULL_DIR / "soln2.tex") as file:
        soln = file.read()
        soln = soln[:-1]
    assert test == soln
