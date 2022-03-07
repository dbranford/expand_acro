import argparse
from expand_acro.parser import AcroParser

import logging

logger = logging.getLogger(__name__)


def expand(file, tmpdir=None, tmpfile=None):
    parser = AcroParser()

    document = parser.input_file(file)

    parser.find_package(document, "acro", remove=True)
    parser.find_acsetup(document, remove=True)

    parser.find_declares(document, remove=False)

    parser.find_preamble_commands(document)
    parser.find_body_commands(document)

    document.construct_texpand()
    document.compile_texpand()

    parser.parse_expanded(document)
    parser.substitute_expanded(document)

    return "\n".join(
        [
            document.docclass,
            document.preamble_converted,
            document.body_converted,
        ]
    )


cli_args = argparse.ArgumentParser(
    description=(
        """Processes a tex file to extract acro commands, find their expansion
        by running tex and extracting the results of the compilation,
        and substitutes them into a resultant tex file"""
    )
)
cli_args.add_argument("texfile")
cli_args.add_argument("-o", "--out-file")
cli_args.add_argument("--in-place", action="store_true")

if __name__ == "__main__":
    args = cli_args.parse_args()
    if args.in_place is True:
        logger.warning(
            "In-place expansion is not yet implemented,"
            "standalone expansion is being performed instead"
        )
    expanded = expand(args.texfile)
    if args.out_file is None:
        print(expanded)
    else:
        with open(args.out_file, "w") as outfile:
            outfile.write(expanded)
