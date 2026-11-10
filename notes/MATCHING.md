# Matching techniques

Compiler idioms that turned a near-match into a match, with the function where each
was seen. armcc-specific; for mwccarm techniques see DQMJ2's `notes/MATCHING.md`,
which does not apply to this compiler.

Empty until the first units are decompiled.

Tools: `tools/asm_compare.py` (one function side by side with the original),
`tools/why_diff.py` (differing rows sorted into register, stack, moved and code
differences) and `tools/permute.py` (random search over source forms of one function;
a heuristic whose mutations come from mwccarm work, and only a score of 0 counts, with
`tools/report_diff.py` and `ninja` as the proof). BigRed's notes on what armlink did to the
code (`notes/BUILD_SYSTEM.md`, "What the linker did to the code") come first when a
call or a branch differs.
