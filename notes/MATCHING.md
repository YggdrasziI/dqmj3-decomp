# Matching techniques

Compiler idioms that turned a near-match into a match, with the function where each
was seen. armcc-specific; for mwccarm techniques see DQMJ2's `notes/MATCHING.md`,
which does not apply to this compiler.

## A local that changes register allocation or load pairing (armcc 4.1)

Reading a value into a local (or binding a local reference) before using it moves where armcc
loads it, which changes register allocation and whether two adjacent loads become one `ldrd`.
Seen in the game's altered Squirrel (2026-11-10):

- `SQArray::Extend` (`squirrel/sqobject.cpp`): `const SQObjectPtr &o = a->_values[i]; Append(o);`
  instead of `Append(a->_values[i])`; the inlined `push_back` then reads `_size` and
  `_allocated` with one `ldrd` (the stock form loads `_allocated` then `_size`).
- `base_array` (`squirrel/sqbaselib.cpp`), through `SQArray::ShrinkIfNeeded` (`sqarray.h`):
  `SQUnsignedInteger cap = _values.capacity();` before the comparison keeps `_allocated` in
  `r0` and moves `_vals` into `r0` for the `sq_vm_realloc` call. The other inlined users of
  `ShrinkIfNeeded` compile the same with either form.

Not solved this way: `array_sort` (`_hsort` inlined). `SQObjectPtr *vals = &a->_values[0];
_Swap(vals[0], vals[i]);` brings it from 9 to 2 differing words (96.6 % in objdiff): the
original loads `b._type` before `ldrd` of `a`, ours the other way round. Swapped operands,
local references, header variants of `_Swap` and 15,000 `permute.py` variants did not fix it.

To test a header change, compile all files with it: a form that fixes one function can break
others (writing `push_back`'s test as `_size >= _allocated` broke 17 matched functions). Note
that `#include "..."` looks in the including file's directory first, so a changed header must
replace the original in a copy of the whole directory, not shadow it with `-I`.

Tools: `tools/asm_compare.py` (one function side by side with the original),
`tools/why_diff.py` (differing rows sorted into register, stack, moved and code
differences) and `tools/permute.py` (random search over source forms of one function;
a heuristic whose mutations come from mwccarm work, and only a score of 0 counts, with
`tools/report_diff.py` and `ninja` as the proof). `tools/reloc_names.py` names the `fn_`/`lbl_` symbols that matched functions call or
refer to, from the same relocation in our object (same offset, type and addend).
BigRed's notes on what armlink did to the
code (`notes/BUILD_SYSTEM.md`, "What the linker did to the code") come first when a
call or a branch differs.

## Library code that is close but not exact: try other CPUs and builds first

A prebuilt library may have been compiled with another `--cpu` and build than the game.
Seen in the CTR-SDK's zlib (2026-11-11, `notes/COMPILER.md`): with the game's flags, many
functions differed by swapped registers or a few `nop`s, which looks like a source change
but was not. `--cpu=MPCoreNoVFP` and RVCT 4.1 b1049 matched them all unchanged.

- Swapped registers over a whole function, the same instructions otherwise: try other
  `--cpu` values (`6K`, `ARM1136J-S`, `MPCoreNoVFP`) before editing the source.
- `nop` (0xE320F000) is MPCore scheduling. `mov r0, r0` (0xE1A00000) is a call armlink
  inlined (`notes/BUILD_SYSTEM.md`). They are not the same and need different fixes.
- One instruction more or less than the original, with the right CPU: try the other
  builds (`compiler_sweep.py` on the file) before rewriting the source.
- Run the sweep per library: set its `armcc_version` and `--cpu` in its `config.libs`
  entry in `configure.py`.
