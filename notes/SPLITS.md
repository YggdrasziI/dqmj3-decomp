# Splits and region map

How `.text`, `.rodata` and `.data` divide into libraries and units, with the evidence
for every boundary. A boundary is a hypothesis until a unit on each side matches.

## Current state

- `config/jpn/splits.txt` claims one unit; every other byte belongs to an automatic
  unit (`auto/<section>_<address>`, 64 KiB grid, see `notes/BUILD_SYSTEM.md`).
- `config/jpn/symbols.txt` comes from `tools/ctr/analyze.py` (2026-11-10): 34,058
  functions (332 Thumb), 14,995 data labels. 127 functions have control flow the
  analysis could not follow; their bounds are not trusted.
- No `[[regions]]` in `config/jpn/config.toml` yet; string pools below.

## Leads for the region map (step 4)

- Thumb functions cluster in 0x00100000-0x0013FFFF (202) and 0x002C0000-0x0033FFFF
  (130): likely runtime / SDK code (as in BigRed). Hypothesis.
- `.text` 0x00640000-0x006C0000 holds data islands (pointer tables, UTF-16 strings such
  as at 0x00660124) between functions.
- Library strings (`notes/COMPILER.md`) give anchors: zlib near 0x0047AFF4,
  `nn::ac` near 0x001ABA78.
- Functions found by the compiler sweeps (`notes/COMPILER.md`): Squirrel 2.2.5 (224,
  named in `symbols.txt`; spread over 0x00154000-0x006AE000, not one block), zlib in 0x00695000-0x006B1000 (11).
- Script bindings: `BattleScriptFunc.cpp` 0x0012D8E0-0x00148AE0 (140 functions),
  `FieldScriptFunc.cpp` 0x00251FE8-0x0025D0A0 (186 functions); bounds of the
  functions that pass the file name, not of the files.

## Network libraries (NEX, PIA): leads (2026-11-10)

Functions that reference a library-specific string (inline literal pool or `.rodata`):

| Marker | Functions | Range |
|---|---|---|
| NEX (`NEX_3_9_1` version string, `Nex*` classes) | 9 | 7 in 0x0040A16C-0x004676B0, plus 0x005DD228 and 0x005DEBEC |
| PIA (`pia sync heap`, `Pia ReceiveThreadStream`, `NatTraverser::`, `RelayRouteManager::`, `Local*Job::`) | 12 | 11 in 0x00457E54-0x0049B6DC, plus 0x00633398 |
| zlib (`inflate`/`deflate` messages) | 4 | 0x0069D6C0-0x006A51E4 |

- Functions that name themselves (`Class::Method` strings, 58 in all `.text`) are all in
  0x0045A168-0x00499C58 and are **not** in mangled-name order
  (`NatTraverser::stopNatSession` before `NatTraverser::startNatPortDetection`; 3 of 7
  pairs ascend in another cluster), unlike the game runs below. Hypothesis: PIA (and
  NEX) are prebuilt archives whose objects keep their own order.
- No known name (game, Squirrel, runtime) lies in 0x003018C8-0x005889F4; the NEX/PIA
  markers are inside that gap.
- Calls (ARM `BL`) from 0x00450000-0x004A0000 go mostly to themselves; their outside
  targets cluster in 0x005B0000, 0x00620000-0x00630000 and 0x00160000. Calls into it
  come mostly from 0x005D0000, 0x00620000 and 0x00630000. So the network code is not
  one block either, or the blocks at 0x005B/0x0062/0x0063 are other library parts. Not
  resolved.

### Call-graph density (`tools/link_density.py`)

Share of the direct calls (ARM and Thumb `BL`/`BLX`) made from a 128 KiB window that
stay in it: about 0.03-0.13 over most of `.text` (game code calls everything), but a
plateau of 0.2-0.54 over 0x003E0000-0x004DFFFF, and 0.4-0.65 over 0x00150000-0x0019FFFF
(dense Squirrel functions). Scoring functions by their links (callers and callees)
into 0x003F0000-0x004C0000 gives sharp edges:

- start: 0.01-0.11 up to 0x003E9248, 0.49 from 0x003E924C, 0.63 from 0x003E9BAC;
- end: 0.32 up to 0x004C81EC, 0.02-0.08 from 0x004C81F0.

So a self-contained block of about 0x003E9A00-0x004C8000 (0.9 MB) holds the NEX
version string and 11 of the 12 PIA markers: likely the network libraries. It makes
6,257 calls inside and 4,074 to 667 functions outside it (runtime, SDK and helpers
placed in the sorted runs). The game-side callers of PIA (0x005D0000,
0x00620000-0x00630000) are outside it.

Refined with a wider core (`--core 0x3E0000-0x4C8000 --group 1`) and the 3DS service
names the code passes to `srv` (`tools/link_density.py`, strings with their user
function):

| Function | Service | Place in the block |
|---|---|---|
| 0x003E0AE4 | `ac:u` (`.rodata` 0x00735C00) | first function linked to the block; none of the 32 functions before it is |
| 0x003E7844 | `cecd:u` | before the NEX/PIA part |
| 0x004A35F0 | `ssl:C` | after the last function that refers to the NEX/PIA data (0x004A5434) |
| 0x004A7598, 0x004A94AC, 0x004AA13C, 0x004AED5C | `boss:U`, `http:C` (twice), `soc:U` | |
| 0x004B1440 | `frd:u` (inline string) | |
| 0x004C6184 | - | last function linked to the block; none of 0x004C6250-0x004C8000 is |

NEX/PIA data: the functions of 0x003F0000-0x004C0000 own several `.rodata`, `.data`
and `.bss` ranges (blocks of 1 KiB referenced at least 80% by them: 0x0073CC00-0x0073E400,
0x00749000-0x0074AC00, 0x007ACC00-0x007AE000, 0x0080FC00-0x00810000, 0x0083B800-0x0083C400,
...), not one contiguous range. Functions referring to them run from 0x003E9F74 to
0x004A5434 (plus 100 outside the block, in game regions).

Hypothesis: the block 0x003E0AE4-0x004C6250 is prebuilt network code in link order:
CTR-SDK clients (`nn::ac`, `nn::cecd`), NEX and PIA, then CTR-SDK clients (`nn::ssl`,
`nn::boss`, `nn::http`, `nn::socket`, `nn::friends`). Edges within a few functions; no
matched unit proves them. Other service clients lie elsewhere: `ndm:u` 0x0010AFE0,
`fs:USER` 0x001132B0, `dsp::DSP` 0x00121C20, `ir:USER` 0x0017FA48.

### Start of `.text` (2026-11-10)

`tools/link_density.py --core 0x100000-0x120000 --range 0x100000-0x140000 --group 48`:

- 0x00100000-0x00103118: 0.03-0.06, but 3,648 links: code called from everywhere
  (start-up and runtime helpers, many Thumb).
- 0x00103120-0x00116E3C: 0.21-0.81, holds the `ndm:u` (0x0010AFE0) and `fs:USER`
  (0x001132B0) clients: likely CTR-SDK code.
- 0x00116EFC-0x0012E5C8: falls slowly (0.35 to 0.10), `dsp::DSP` client at 0x00121C20;
  then 0.00-0.04 from 0x0012E65C (the `BattleScriptFunc.cpp` bindings, 0x0012D8E0).

No sharp edge here, unlike the network block. The `ir:USER` client (0x0017FA48) lies
inside a name-sorted run (0x0017BDD0-0x00186F4C): either some SDK code is sorted with
the game, or that client is game code. Open.

No `[[regions]]` from these: no bound is proven.

## String pools (2026-11-10)

armcc 4.1 b921 puts strings that data refers to in mergeable `.conststring` /
`.constwstring` sections (checked by compiling a table of `const char*` and
`const wchar_t*` with the project's flags), and armlink merged each into one pool.
Both are in `config.toml`:

| Pool | Range | Evidence |
|---|---|---|
| `.conststring` | 0x007B1D7C-0x007C448E (0x12712) | 3,859 strings, all text, no duplicate. 0xFF (armlink's fill) right before and after. Inside, runs of strings sorted by the string read backwards (one run per input section: Squirrel's `.c` ... `dummy` is exactly the `base_funcs` strings), some packed, some 4-aligned with zero padding, 0xFF between sections. armlink's rule (whole string, else the tail of the host that comes last read backwards, `tools/ctr/strpool.py`) gives 2,321 of the 2,322 string pointers in `.data`. The exception: 0x007E2C44 points to `w_00` inside `arrow_00` (0x007B2E74), where the rule picks `scout_arrow_00`; `arrow_00` itself was not merged into `scout_arrow_00`, so the merge was not one global pass (per group of sections?): open. The first bound found (0x007C1724-0x007C3D2E) was one run inside it. |
| `.constwstring` | 0x007CAB34-0x007CC0A2 (0x156E) | 168 UTF-16 strings (`rom:/data/Community/CommunityPrize.nut`, ...), packed, no duplicate, none the tail of another, each pointed to once at its start (167 from data, 1 from `.text`); 0xFF padding (armlink's fill) right before and after, so one section of its own. |

Other strings in `.rodata` are 4-aligned with zero padding between them (compiler
`.constdata`), or in small sections that 0xFF padding separates (for example many
UTF-16 `rom:/data/...` paths at 0x007C4490-0x007C6900, one section each).
`squirrel/sqbaselib.cpp`'s `.data` (144 string pointers) matches through the narrow pool.

### Squirrel's strings (2026-11-10)

0x007C4031-0x007C421C holds Squirrel's strings in runs, one per `.conststring` section of
`sqbaselib.cpp` (`.c` ... `dummy`, `rawdelete` ... `rawset`, ...), each sorted by the string read
backwards; zlib's `z_errmsg` strings (`stream end` ... `insufficient memory`) come right before, C++
library messages (`%s: bad locale name` ...) after. Strings already in the pool earlier are left out
and point there: `clear` is the tail of `judge_clear` (0x007B4606), `pop` of `apeal_pop` (0x007B4036),
`t` is the game's string at 0x007B3BDC.

## Static initializer table (2026-11-10)

`[init_array]` in `config.toml`: 0x007CC1F8-0x007CE2DC (0x20E4), the end of `.rodata`.
Each of its 2,105 words is the offset from the word to a function (+1 for 3 Thumb
ones): the relative form of `.init_array` that `linker.py` reproduces. Before
0x007CC1F8 the words (8, 0x43, -8, 0) do not point into `.text`. All 2,105 targets
are function starts in `symbols.txt` once two bounds are fixed (0x006602D0 started 4
bytes early, inside the literal pool of `fn_006602C0`; 0x0066FD74-0x0066FDA0 is a
table of 11 addresses, not code). Proven for one entry by a matched unit:
0x007CE0B0 is `__sti___11_sqstate_cpp` (0x00655B48) of `squirrel/sqstate.cpp`.

The initializers (one per source file that has static objects with constructors)
lie in 0x00650000-0x0069FFFF. armcc names them `__sti___<n>_<file>`; in the image
they have no names. The table keeps the order armlink read the objects in; using
that order to group units is not tried yet.

## Code order: runs sorted by mangled name (2026-11-10)

Known function names (273 in `symbols.txt` plus the 326 script bindings, named by the
`__FUNCTION__` string they pass) sorted by address fall into 26 runs in which the
mangled names ascend, for example:

- `FieldScriptFunc.cpp`: its 186 bindings at 0x00251FE8-0x0025D0A0 are in strict
  mangled-name order (185 of 185 pairs ascend: `_Z10ChangeMap_P4SQVM` ... `_Z9GetAlpha_P4SQVM`);
  the run goes on with Squirrel functions up to `SQNativeClosure::Release` at 0x0026BEAC.
- `BattleScriptFunc.cpp`: 138 of 139 pairs ascend at 0x0012D8E0-0x00141E40; the run ends
  with `sq_open` (Squirrel).
- Squirrel's `sqapi.cpp` functions are in several runs (`sq_call` ... `sq_writeclosure`
  at 0x00154380-0x00154974, `sq_compile` ... `sq_set` at 0x00160EC8-0x001613CC).

So within a run, game and library functions are mixed in name order, and a library is
not one address range: `[[regions]]` by address can not separate Squirrel from the game
code around it. The 26 run bounds are only where two known names are out of order,
not proven unit bounds.

What delimits a run (tested 2026-11-10 on 598 known names, with the script bindings
named from their `__FUNCTION__` string):

- The sort key is the armcc section name: with `t.` for template instances (as armcc
  names them, checked on our Squirrel objects) and `i.` for the rest, runs drop from
  26 to 24, and every template instance (`sqvector<...>`) sits at the end of a run.
  Within a run, plain `strcmp` order: `_Z...`, then `__aeabi_*`, then C names (`sq_*`).
- Other keys fit worse: case-folded names 27-30 runs, demangled names 128-130.
- Runs interleave function by function, not object by object: `sq_pop` (0x0016CC68,
  `sqapi.cpp`), `SQVM::Pop(int)` (0x0016CC80, `sqvm.cpp`, a new run), `sq_pushroottable`
  (0x0016CCC4), `SQVM::Push` (0x0016CCCC, a new run). So not sorted objects (or
  partial links) laid end to end.
- A call-graph property as primary key (call height, number of callees, number of
  callers, ascending or descending, then the name) gives 98-200 runs: rejected.
- `armlink --tailreorder` (`notes/BUILD_SYSTEM.md`) moves a tail-called function right
  after its caller, out of its sorted place: 1,283 ARM functions end with the
  `mov r0, r0` that replaced the branch and fall into the next one. Leaving those
  callees out removes 3 breaks (26 to 23 runs): `sq_pop` -> `SQVM::Pop(int)`,
  `sq_pushroottable` -> `SQVM::Push`, `sq_collectgarbage` ->
  `SQSharedState::CollectGarbage`. So a unit's functions are not all contiguous: a
  callee from another file can sit in the middle of a run.
- armlink is not in decomp.me's `armcc.zip` (and RVCT 4.1 is not available), so the
  sort options (`--sort=...`) can not be tried. The other breaks stay open.

## Units

| Unit | Range | Content | Status |
|---|---|---|---|
| `game/FieldScriptFunc.cpp` | `.text` 0x002546FC-0x00254784, `.rodata` 0x00725800-0x0072580F | `SetFogDensity_` and its `__FUNCTION__` string | Matching (2026-11-10) |
| `squirrel/sqdebug.cpp` | 0x0018E3C4-0x0018E704, 0x00197438-0x0019774C, 0x006AE8CC-0x006AE9C4 | 7 functions (`SQVM::PrintObjVal`, both `SQVM::Raise_Error`, `Raise_IdxError`, `Raise_CompareError`, `Raise_ParamTypeError`, `sq_stackinfos`); `sq_getfunctioninfo` is not in the game (removed by armlink) | Matching (2026-11-10) |
| `squirrel/sqstate.cpp` | 13 `.text` ranges, `.rodata` 0x007CE0B0-0x007CE0B4 (its `.init_array` entry), `.data` 0x008108F8-0x00810920 | 14 functions with `__sti___11_sqstate_cpp`, and `_null_`, `_true_`, `_false_`, `_one_`, `_minusone_` | Matching (2026-11-10) |
| `squirrel/sqtable.cpp` | 8 `.text` ranges, `.rodata` 0x007A7E34-0x007A7E54 (`_ZTV7SQTable`) | 14 functions and the vtable; its slots named `SQTable::~SQTable` and `SQTable::Finalize`; `D0` is 0 in the original (removed) | Matching (2026-11-10) |
| `squirrel/sqbaselib.cpp` | 31 `.text` ranges (without `array_sort` and `base_array`), `.rodata` 0x0076B3D4-0x0076B42B (`.constdata`), `.data` 0x00820070-0x00820650 in 11 ranges, one per table (`base_funcs` and the 10 delegate tables, a section each) | 59 functions; 21 named from the delegate tables (the slot next to each name string, as for vtables), `sq_suspendvm` and `tolower` from their calls | NonMatching: all 59 at 100 %; not claimed, game variants `base_array` (98.6 %, the inlined `sqvector` resize loads its arguments in another order, like `SQArray::Extend`) and `array_sort` (89.3 %, swaps with `ldrd`/`strd` instead of VFP); `.constdata`, `.data` and its strings at 100 % |
| `squirrel/sqlexer.cpp` | 4 `.text` ranges, `.rodata` 0x0076B458-0x0076B484 (`.constdata`: `Invalid character`, `missing "*/" in comment`) | 9 functions with `ReadNumber`, `ReadString`, `Lex`; the other functions of the file are inlined; `toupper` (0x00102AFC) and `strtoul` (0x00102C10) named from their calls | Matching (2026-11-10) |
| `squirrel/<file>.cpp` (7 other files, `libs/squirrel/`) | 125 `.text` ranges | the functions the sweep found, plus the functions named by the calls of matched code (`tools/reloc_names.py`) that compile to the same code | NonMatching: 223 of 229 at 100 % in objdiff with relocation targets compared; the 6 others refer to a long string literal (`.constdata`) or a vtable whose `.rodata` is not claimed yet. 13 named functions differ from the 2.2.5 source (game changes, not claimed): `sq_setparamscheck`, `SQClass::CreateInstance`, `SQCompiler::{Expression, PrefixedExpr, LogicalAndExp, Compile}`, `SQFuncState::~SQFuncState`, `SQArray::Extend`, `SQVM::{CallNative, Pop(), Push, ObjCmp, Execute}` |
