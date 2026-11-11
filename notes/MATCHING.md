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

## Script bindings (FieldScriptFunc.cpp, 2026-11-11)

The 186 bindings follow one shape: one getter per argument (`sq_get*` at -n ... -1, each
error path on its own line, set with `#line`), one call on the field object, then
`return 0` or a `sq_push*` of the result and `return 1`. They were written by a script
from the disassembly, then the exceptions by hand.

- Load the object into a local first: `void* self = lbl_007E7808; fn_X(self, value);`.
  Passing `lbl_007E7808` directly schedules the loads differently, and a `bool` parameter
  then compiles to `movne r1, #1` + `moveq r1, #0` in a new register instead of the
  original `ldr r1, [sp]; cmp r1, #0; ...; movne r1, #1`.
- Read the argument types from the code around the call: `and rN, rN, #0xff` is an
  `unsigned char` parameter, `sxtb` a `signed char`, `sxth` a `short`, `movne`/`moveq`
  a `bool`, a plain load an `int` (or `SQBool` when the getter is `sq_getbool`), and
  `fsitos` an `int` passed to a `float` parameter. Arguments past r3 are stored to
  `[sp, #0]`...: look for the conversion of the register stored there, and take only the
  last write of a register before the call.
- A function returning a vector of three floats returns it in `s0`-`s2` (VFP ABI,
  `fstmias r2, {s0, s1, s2}` after the call); one returning `ldmia r0` returns a pointer.
- Two adjacent float locals copied into a struct with `ldrd`/`strd`: with b921, armcc does
  it for an inline member that assigns the fields (`offset.Set(0.0f, a1, a2)`). With 5.04
  the same member gives the original stack layout but a VFP copy, and assigning a
  two-float struct gives the `ldrd`/`strd` copy with the vector below the arguments
  (`SetTalkCameraEyeOffset_`, 93.9 %). armcc does not follow the declaration order of
  locals when it lays out the stack: moving declarations did not change it.

### More from BattleScriptFunc.cpp (2026-11-11)

Both binding files match better with ARM Compiler 5.04 b82 than with 4.1 b921
(`notes/COMPILER.md`): try 5.04 on a game file before rewriting a function.

- `sxtb` then `and #0xff` on one argument: a `signed char` local passed to an
  `unsigned char` parameter: `signed char idx = a0; void* self = lbl_007E7808;
  fn_X(self, idx, ...)`.
- A `bool` built with `cmp rN, #1; movne rN, #0` (`moveq rN, #1` when the register is not
  already 1): the source compares the `SQBool` with 1 (`a1 == 1`). `cmp rN, #0;
  movne rN, #1` is the plain conversion (`a1 != 0`, or `a1` to a `bool` parameter).
- Arguments loaded before the object pointer (`ldr r0, [sp, #4]; ldr r1, [sp]; sxtb ...;
  ldr r0, =lbl`): store the result in a local before pushing it (`int r = fn_X(self, a0,
  a1); sq_pushinteger(v, r);`).
- Byte temporaries passed by address below the getter locals (`strb r0, [sp, #4]; ...;
  mov r1, sp`): `unsigned char` locals declared before the getter locals, assigned in
  reverse order (`y = a1; x = a0;`), passed to `const unsigned char&` parameters.
- Constant arguments (`mov r2, #1`) after the script arguments: one callee shared by
  several bindings with a kind number (`AddBattleEventMessage_` 0, `...FeatMessage_` 1,
  `...OtherMessage_` 2).
- Floats converted with `ftosis` and stored next to each other, then their address passed:
  an `int` array initialized from the floats.
- Not solved: an `unsigned char` argument where the original loads the object pointer
  into a scratch register before masking the index, then moves it to r0
  (`ldr r1, =lbl; ldr r0, [sp]; ldr r2, [r1]; and r1, r0, #0xff; mov r0, r2`). 21 bindings
  of `BattleScriptFunc.cpp`. Tried with b921 and 5.04: self or direct, casts, `& 0xff`,
  locals of each type, enums, inline wrappers and members, references, a `volatile` or
  reference self, result locals, -O levels.
