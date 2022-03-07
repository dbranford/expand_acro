from expand_acro.misc import strip_comments
from pathlib import Path
import dataclasses
import pdftotext
import subprocess
import tempfile

AC_PLACEHOLDER_START = r"<+"
AC_PLACEHOLDER_END = r"+>"


class Document:
    def __init__(self, docclass="", preamble="", body="", source=None):
        self.docclass = docclass
        self.preamble = preamble
        self.body = body
        self.docclass_converted = docclass
        self.preamble_converted = preamble
        self.body_converted = body
        self.docclass_stripped = strip_comments(self.docclass)
        self.preamble_stripped = strip_comments(self.preamble)
        self.body_stripped = strip_comments(self.body)

        self.packages = list()
        self.declares = list()
        self.ac_ids = list()
        self.acsetup = list()
        self.commands_preamble = list()
        self.commands_body = list()

        self.ac_placeholder_start = AC_PLACEHOLDER_START
        self.ac_placeholder_end = AC_PLACEHOLDER_END

        self.compiler = Compiler()

    def construct_texpand(self):
        texpand_document = r"\RequirePackage[T1]{fontenc}" + "\n"
        texpand_document += self.compiler.docclass
        for pkg in self.packages:
            texpand_document += "\n" + pkg
        texpand_document += "\n" + r"\acsetup{" + ",".join(self.acsetup) + "}"
        for declare in self.declares:
            texpand_document += "\n" + declare
        for uuid, macro in self.commands_preamble:
            texpand_document += (
                "\n"
                + self.ac_placeholder_start
                + str(uuid)
                + self.ac_placeholder_end
                + macro
                + self.ac_placeholder_start
                + str(uuid)
                + self.ac_placeholder_end
            )
        texpand_document += "\n" + r"\begin{document}"
        for uuid, macro in self.commands_body:
            texpand_document += (
                "\n"
                + self.ac_placeholder_start
                + str(uuid)
                + self.ac_placeholder_end
                + macro
                + self.ac_placeholder_start
                + str(uuid)
                + self.ac_placeholder_end
            )
        texpand_document += "\n" + r"\end{document}"

        self.texpand_document = texpand_document

    def compile_texpand(self):
        tmp_tex_dir = tempfile.TemporaryDirectory()
        tmp_tex_path = Path(tmp_tex_dir.name) / (self.compiler.tmp_file_name + ".tex")
        tmp_pdf_path = Path(tmp_tex_dir.name) / (self.compiler.tmp_file_name + ".pdf")

        with tmp_tex_path.open("x") as f:
            f.write(self.texpand_document)

        for binary in self.compiler.compilation:
            subprocess.run([binary, tmp_tex_path], cwd=tmp_tex_dir.name)

        with tmp_pdf_path.open("rb") as f:
            pdf = pdftotext.PDF(f)
            pdf = ("\n").join(pdf)

        self.texpand_compiled = pdf


@dataclasses.dataclass
class Compiler:
    # Should branch out to arara/latexmk
    compilation: list[str] = dataclasses.field(
        default_factory=lambda: ["pdflatex", "pdflatex"]
    )
    docclass: str = r"\documentclass{standalone}"
    tmp_file_name: str = "expand_acro_tmp"
