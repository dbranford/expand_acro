A script to parse a tex file for uses of the [acro](https://ctan.org/pkg/acro) package, compile to find the **textual** expansions (formatting is lost) and substitute into a revised dependence-free (currently the preamble is not affected) tex file.
This is in no way better than just using Clemens Niederberger's acro package, but might be better than whatever journals do to tex source during copy-editing.

Known issues:
- Acronym-specific formatting is not translated
- \printacronyms not supported
- Preamble contents are retained
- Whitespace is lost (or possibly gained), particularly after `\documentclass` and before `\begin{document}`.
- Comments surrounded by acro-commands may be undesirably preserved
- Some acro commands in comments may be affected

Requirements:
- pyparsing >= 3.0.0
- pdftotext
