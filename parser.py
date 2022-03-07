from expand_acro.document import Document
import expand_acro.patterns as patt
import pyparsing as pp
import uuid


class TexParser:
    def __init__(self):
        self.uuid_fn = uuid.uuid4

    def input_file(self, file):
        docclass, preamble, body = patt.tex.document.parse_file(file)
        return Document(docclass, preamble, body, source=(file, "file"))

    def input_string(self, string):
        docclass, preamble, body = patt.tex.document.parse_string(string)
        return Document(docclass, preamble, body, source=(string, "string"))

    def find_package(self, document, pkg, fail=None, remove=False):
        """Will always return an invocation of the package, if none are found no options are provided.
        Currently \\usepackage is enforced in the returned invocation.
        This could clash (whether found or not) where first loaded by a class/package with different options.
        Similarly, no detection of \\PassOptionsToPackage is done"""
        try:
            pkg_match = (pp.Suppress(...) + patt.tex.reqpkg(pkg)).parse_string(
                document.docclass_stripped
            )
            pkg_match = pkg_match.as_list()
            pkg_match[0] = r"\usepackage"
        except pp.ParseException:
            try:
                pkg_match = (pp.Suppress(...) + patt.tex.usepkg(pkg)).parse_string(
                    document.preamble_stripped
                )
                pkg_match = pkg_match.as_list()
            except pp.ParseException:
                if callable(fail):
                    pkg_match = fail(pkg)
                elif isinstance(fail, str):
                    pkg_match = fail
                elif fail is None:
                    pkg_match = [r"\usepackage", "{" + pkg + "}"]
        document.packages.append("".join(pkg_match))


class AcroParser(TexParser):
    def __init__(self):
        super().__init__()
        self.use_ac_ids = False

    def find_acsetup(self, document, remove=False):
        acsetup = patt.acro.acsetup.search_string(
            document.docclass_stripped + document.preamble_stripped
        )
        acsetup = acsetup.as_list()
        document.acsetup = [setup[0][1:-1] for setup in acsetup]

    def find_declares(self, document, remove=False):
        pattern = patt.acro.DeclareAcronym.add_parse_action(
            lambda toks: document.declares.append(toks[0])
        )
        pattern.add_parse_action(lambda toks: document.ac_ids.append(toks["id"]))
        pattern.search_string(document.docclass_stripped + document.preamble_stripped)

    def find_commands_actions(
        self, document, commands, printable, noprintable, weird, aux
    ):
        if self.use_ac_ids is True:
            patt_ac_printable = patt.acro.ac_printable(document.ac_ids)
            patt_ac_noprintable = patt.acro.ac_noprintable(document.ac_ids)
            patt_ac_aux = patt.acro.ac_aux(document.ac_ids)
            patt_ac_weird = patt.acro.ac_weird(document.ac_ids)
        else:
            patt_ac_printable = patt.acro.ac_printable()
            patt_ac_noprintable = patt.acro.ac_noprintable()
            patt_ac_aux = patt.acro.ac_aux()
            patt_ac_weird = patt.acro.ac_weird()

        def common_parse_action(toks, return_placeholder, transform):
            return self.parse_uses(
                toks,
                commands,
                document.ac_placeholder_start,
                document.ac_placeholder_end,
                return_placeholder=return_placeholder,
                transform=transform,
            )

        pattern_actions = []
        if printable is True:
            pattern_actions.append(
                (
                    patt_ac_printable,
                    lambda toks: common_parse_action(
                        toks,
                        return_placeholder=True,
                        transform=True,
                    ),
                )
            )
        if noprintable is True:
            pattern_actions.append(
                (
                    patt_ac_noprintable,
                    lambda toks: common_parse_action(
                        toks,
                        return_placeholder=False,
                        transform=True,
                    ),
                )
            )
        if aux is True:
            pattern_actions.append(
                (
                    patt_ac_aux,
                    lambda toks: common_parse_action(
                        toks,
                        return_placeholder=False,
                        transform=False,
                    ),
                )
            )
        if weird is True:
            pattern_actions.append(
                (
                    patt_ac_weird,
                    # This is probably not enough for weird
                    lambda toks: common_parse_action(
                        toks,
                        return_placeholder=True,
                        transform=True,
                    ),
                )
            )
        return pattern_actions

    def find_preamble_commands(self, document):
        pattern_actions = self.find_commands_actions(
            document=document,
            commands=document.commands_preamble,
            printable=False,
            noprintable=True,
            weird=True,
            aux=True,
        )
        document.preamble_converted = self.transform_commands(
            document.preamble_converted, pattern_actions
        )

    def find_body_commands(self, document):
        pattern_actions = self.find_commands_actions(
            document=document,
            commands=document.commands_body,
            printable=True,
            noprintable=True,
            weird=True,
            aux=True,
        )
        document.body_converted = self.transform_commands(
            document.body_converted, pattern_actions
        )

    def transform_commands(self, text, pattern_actions):
        patterns = []
        for pattern, action in pattern_actions:
            pattern.set_parse_action(action)
            patterns.append(pattern)

        transformed_text = (pp.Or(patterns)).transform_string(text)
        return transformed_text

    def parse_uses(
        self,
        matched,
        uses,
        placeholder_start,
        placeholder_end,
        return_placeholder,
        transform,
    ):
        uuid_string = self.uuid_fn()
        uses.append((uuid_string, matched[1]))
        placeholder = ""
        if return_placeholder:
            placeholder = placeholder_start + str(uuid_string) + placeholder_end
        if transform:
            return placeholder

    def parse_expanded(self, document):
        expansions = []
        for uuid_string, macro in document.commands_body:
            placeholder = (
                document.ac_placeholder_start
                + str(uuid_string)
                + document.ac_placeholder_end
            )
            pattern = pp.QuotedString(
                placeholder,
                multiline=True,
            )
            matched = pattern.search_string(document.texpand_compiled)
            if len(matched) != 1:
                if len(matched) > 1:
                    raise ValueError(
                        f"Unique match failed for expanded form of {macro}"
                    )
                if len(matched) == 0:
                    raise ValueError(f"Match failed for expanded form of {macro}")
            expansions.append((uuid_string, matched[0]))
        document.commands_body_converted = expansions

    def substitute_expanded(self, document):
        body = document.body_converted
        for uuid_string, macro in document.commands_body_converted:
            pattern = pp.Literal(
                document.ac_placeholder_start
                + str(uuid_string)
                + document.ac_placeholder_end
            )
            pattern.set_parse_action(lambda x: macro)
            body = pattern.transform_string(body)
        document.body_converted = body
