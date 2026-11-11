# Splits and region map

How `.text`, `.rodata` and `.data` divide into libraries and units, with the evidence
for every boundary. A boundary is a hypothesis until a unit on each side matches.

## Current state

- `config/jpn/splits.txt` claims one unit; every other byte belongs to an automatic
  unit (`auto/<section>_<address>`, 64 KiB grid, see `notes/BUILD_SYSTEM.md`).
- `config/jpn/symbols.txt` comes from `tools/ctr/analyze.py` (2026-11-10), fixed by hand
  since: 34,020 functions (332 Thumb) after the bounds fixes of 2026-11-11 ("Function
  bounds" below). 39 functions still have control flow the analysis could not follow.
- `[[regions]]` in `config/jpn/config.toml`: three blocks ("Region map" below); string
  pools below.

## Leads for the region map (step 4)

- Thumb functions cluster in 0x00100000-0x0013FFFF (202) and 0x002C0000-0x0033FFFF
  (130): likely runtime / SDK code (as in BigRed). Hypothesis.
- `.text` 0x00640000-0x006C0000 holds data islands (pointer tables, UTF-16 strings such
  as at 0x00660124) between functions.
- Library strings (`notes/COMPILER.md`) give anchors: zlib near 0x0047AFF4,
  `nn::ac` near 0x001ABA78.
- Functions found by the compiler sweeps (`notes/COMPILER.md`): Squirrel 2.2.5 (224,
  named in `symbols.txt`; spread over 0x00154000-0x006AE000, not one block), zlib in 0x00694000-0x006B2000, two copies interleaved by the name sort (CTR-SDK 1.2.7 and 1.2.5, `notes/COMPILER.md`).
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
| zlib 1.2.5 (string `1.2.5` at 0x0073C75C) | 1 | 0x0040F940, calls the zlib 1.2.5 copy (`deflateInit2_` 0x006A3248) |

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

No `[[regions]]` from these: no bound is proven (the region map below keeps the C library
before 0x00104AF8 only).

## Region map (2026-11-11)

### Sorted runs and link-order blocks

Most of `.text` is in runs sorted by name ("Code order" below), where game functions and
library functions compiled with the game alternate one function at a time: Squirrel
(0x00154000-0x006AE000), the game's script bindings, sead-like functions found by
compiling BigRed's sources (`sead::Heap`, `sead::ExpHeap`, `sead::ThreadMgr` at
0x005BDDE0-0x005C0908 in mangled-name order, `sead::ExpHeap` const methods at 0x0064B6F8;
names from another game, leads only), both zlib copies (0x00694968-0x006B0DD0, by name:
`build_tree` ... `flush_pending`, then `_tr_align` ... `zcfree`, then `scan_tree`,
`send_tree`, `updatewindow`), and the 2,102 ARM static initializers (0x00650000-0x00694620,
right before `build_tree`). An address range there can not be given to one library, so it
is attributed unit by unit.

Three blocks keep their own order and are in `[[regions]]`:

| Region | Range | Category | Evidence | Edges |
|---|---|---|---|---|
| C library and start-up | 0x00100000-0x00104AF8 | `sdk` | `__ctr_start` (entry), RVCT C library functions (`__aeabi_vec_dtor`, `memcmp`, `strtol`, `__2sprintf`, `toupper`, `strtoul`, `__c89vsprintf`, `strstr`, `__cxa_pure_virtual`) out of name order; 202 of the 332 Thumb functions (the game is ARM) | start: the entry point. End: the last Thumb function. After it, `fn_00104AF8` (ARM) is called only from the C library and calls it, and 0x00104BC4-0x00104C9C are start-up functions called from the C library, one with the CTR-SDK marker call (0x00104C54): SDK start-up code that goes on with no sharp edge ("Start of `.text`" above). Not in a region. |
| C library | 0x002FE18C-0x003041E0 | `sdk` | `__rt_ctype_table`, `strlen`, `malloc`, `__aeabi_idivmod`, `__aeabi_memcpy`, `__aeabi_memclr4`, `free`, `tolower`, `__aeabi_atexit`, out of name order; the other 130 Thumb functions | start: `__rt_ctype_table`; `fn_002FE0BC` before it and `fn_002FE1A0` after it are in a vtable (`lbl_00782070`) and call game code, so the edge is within one or two functions. End: the last Thumb function; `fn_00304280`, after it, is in a vtable and calls game code. |
| Network libraries | 0x003E0AE4-0x004C6250 | `net` | call-graph block ("Network libraries (NEX, PIA): leads" above): CTR-SDK clients of `ac:u`, `cecd:u`, `ssl:C`, `boss:U`, `http:C`, `soc:U`, `frd:u`; NEX (`NEX_3_9_1`) and PIA strings; NEX UTF-16 messages (`prudp:/`, `Transport Buffer Thread`, `ConnectionManager`) in 0x003EA430-0x004571D4 | first and last function linked to the block, within a few functions. The SDK clients and NEX/PIA are not separated (no sharp edge between them). |

NEX and PIA strings outside the block, in name-sorted code: `PiaInet Automatch`
(0x005CDF8C), `PiaInet Matchmake` (0x005D06BC), `Community`/`PersistentGathering`
(0x0062BC3C), `Failed:PrepareGetObject`/`PreparePostObject` (0x006B9D00-0x006BBCC8):
likely the game's use of these libraries (wide strings passed to NEX), not the libraries.

All 332 Thumb functions are in the two C-library regions. Attribution by address is only
possible for these three blocks; the sorted runs are attributed per unit.

### Function bounds (2026-11-11)

`tools/ctr/analyze.py --dry-run` listed 134 functions with control flow it could not follow.
In 89 of them, an `ldr` loads a literal after the start of the next function, and nothing
else refers to that start (no call, no pointer, from the relocations of the split objects).
Every one has inline UTF-16 strings between its code and its pool (`rom:/data/...`,
`http://`, NEX messages), which the analysis read as one character, so the next function
was started in the strings. Fixed in `symbols.txt`: each of the 89 now ends at the end of
its pool, the 89 false starts are removed, and 51 functions that start right after a pool
(inside the old false start) are added; all 140 walk cleanly with their new bounds. The
analysis reads those strings now (`notes/BUILD_SYSTEM.md`). The 39 left:

- 21 in the two C-library regions, Thumb mostly: their pool is after the next function,
  which is called from elsewhere (0x0010119C's pool at 0x00101660 is after `fn_001013B0`).
  Hypothesis: the C library is not built with one section per function, so a pool may
  follow several functions. Bounds kept.
- 18 others, not reviewed one by one: three where the start inside the pool is called
  from elsewhere (0x0037E9B0, 0x005CE4D0, 0x005D0A90), loads before the function start
  (0x001BF5AC, 0x003B303C, 0x003FB0D8, 0x003FB13C, 0x005CEE4C), switch tables that do
  not decode (0x0019B060, 0x002BE59C, 0x0032C960), data islands (0x0065F998, 0x0066F684,
  0x0066FD6C), and 0x00136794, 0x00372108, 0x0037E5D8, 0x00552E08, 0x005CD1E8, 0x00650560,
  flagged while walking another function.

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
| `squirrel/sqbaselib.cpp` | 31 `.text` ranges (without `array_sort`), `.rodata` 0x0076B3D4-0x0076B42B (`.constdata`), `.data` 0x00820070-0x00820650 in 11 ranges, one per table (`base_funcs` and the 10 delegate tables, a section each) | 60 functions; 21 named from the delegate tables (the slot next to each name string, as for vtables), `sq_suspendvm` and `tolower` from their calls | NonMatching: all 60 at 100 %, `base_array` with the altered `SQArray::ShrinkIfNeeded` (`sqarray.h`); not claimed, game variant `array_sort` (best form 96.6 %, `notes/MATCHING.md`); `.constdata`, `.data` and its strings at 100 % |
| `squirrel/sqlexer.cpp` | 4 `.text` ranges, `.rodata` 0x0076B458-0x0076B484 (`.constdata`: `Invalid character`, `missing "*/" in comment`) | 9 functions with `ReadNumber`, `ReadString`, `Lex`; the other functions of the file are inlined; `toupper` (0x00102AFC) and `strtoul` (0x00102C10) named from their calls | Matching (2026-11-10) |
| `squirrel/<file>.cpp` (7 other files, `libs/squirrel/`) | 127 `.text` ranges; `sqcompiler.cpp`'s `.rodata` 0x0074AF64-0x0074B058 (`.constdata`: the 8 operator tables of `SQCompiler` and its long error strings); the `.constdata` of `sqobject.cpp` (0x0074B058-0x0074B14B, type names) and `sqvm.cpp` (0x0074B14C-0x0074B2B7, error strings), which follow `sqcompiler.cpp`'s, `sqfuncstate.cpp` (0x0076B42C-0x0076B455, between `sqbaselib.cpp`'s and `sqlexer.cpp`'s) and `sqapi.cpp` (0x0073E74C-0x0073E75F), each found once in the image with 0xFF fill after it; `_ZTV4SQVM` 0x007A7B2C-0x007A7B48; the vtables compiled in `sqobject.cpp` (`SQGenerator` 0x00779608, `SQRefCounted` 0x0077A180, `SQFunctionProto` and `SQNativeClosure` 0x0077B570-0x0077B5A0, `SQArray` 0x007A7DFC, `SQString` 0x007A8280, `SQClosure` and `SQWeakRef` 0x007A8748-0x007A8778), `SQDelegable`'s and `SQUserData`'s are not in the image; `sqclass.cpp`'s `.rodata` 0x0077905C-0x0077907C (`_ZTV10SQInstance`) and 0x007A7E18-0x007A7E34 (`_ZTV7SQClass`, just before `_ZTV7SQTable`), each found once in the image from the compiled vtable | the functions the sweep found, plus the functions named by the calls of matched code (`tools/reloc_names.py`) that compile to the same code | NonMatching: 185 of 186 at 100 % in objdiff with relocation targets compared; `SQInstance::Finalize` (98.8 %: r2 and r3 swapped in the inlined `SQObjectPtr::operator=` of its loop); the destructors of `SQArray`, `SQClosure`, `SQGenerator`, `SQWeakRef`, `SQClosure::Finalize`, `__cxa_pure_virtual` (pure slot of `_ZTV12SQRefCounted`) and `sqvector<SQObjectPtr>::~sqvector` (called by those destructors; a template instance, claimed by `sqobject.cpp` though any object has a copy) are named from the vtables; `SQString::Release` (0x0022E208) sits between two `sqstate.cpp` ranges; `sqobject.cpp` links as `Matching` but stays `NonMatching`: `SQGenerator::Resume` is not found (its callers `SQVM::Execute` and `FOREACH_OP` are game changes not claimed); `SQClass::~SQClass`, `SQInstance::~SQInstance`, `SQInstance::Finalize` and `SQVM::~SQVM` are named from the vtable slots, `SQRefCounted::~SQRefCounted` is claimed. Named, not claimed (register choices in the inlined `sqvector` code, like `Factor`): `SQFuncState::SetStackSize` (99.0 %), `BuildProto` (97.6 %). No unit is `Matching` while a function of its source is not claimed: in-class methods are COMDAT (inline), so the linker would keep the original bytes of an unclaimed one without error. named functions not claimed: game changes `sq_setparamscheck`, `SQClass::CreateInstance` (1 word), `SQCompiler::{Expression, LogicalAndExp (2 words)}`, `SQFuncState::~SQFuncState`, `SQVM::{CallNative, Pop(), Push, ObjCmp, Execute}`, and `SQCompiler::Statement` and `Factor`, which differ in size from the source; `SQCompiler::Compile` (its calls to `SQFuncState::GetStackSize` inlined by armlink, `inlined_functions` in `config.toml`), `PrefixedExpr` and `CreateFunction` are claimed; `SQCompiler::ParseTableOrClass` (32 words: registers and stack slots, like `Factor`) and `LogicalAndExp` (2 words) are not; `SQArray::Extend` is claimed with its altered form |
| `zlib/{adler32,crc32,deflate,inffast,inflate,inftrees,trees,zutil}.c` (`libs/zlib/`, zlib 1.2.7, 4.1 b1049, `--cpu=MPCoreNoVFP`) | 24 `.text` ranges (`config/jpn/splits.txt`), all in 0x00694968-0x006B0CA8 | the CTR-SDK copy only, 32 functions: `zcalloc`, `zcfree`, `deflateInit2_`, `inflateInit2_` (with the call to `fn_inline_00104C54`, a name of our convention, `notes/COMPILER.md`), `adler32`, `crc32`, `crc32_big`, `deflate`, `deflate_fast`, `deflate_slow`, `deflate_stored`, `fill_window`, `flush_pending`, `deflateBound`, `deflateEnd`, `deflateReset`, `inflate_fast`, `inflate`, `inflateEnd`, `inflateInit_`, `inflateReset`, `updatewindow`, `inflate_table`, `build_tree`, `compress_block`, `scan_tree`, `send_tree`, `_tr_align`, `_tr_flush_bits`, `_tr_flush_block`, `_tr_init`, `_tr_stored_block`; the `mov r0, r0` word in front of an exported function is left to the automatic unit; `deflateInit2_` (0x0069D2AC) falls through into `deflateReset` (the analysis had one function of 0x410 bytes); data named from the references of `inflate` and `deflate` (`lenfix`, `distfix`, `order`, `configuration_table`, `z_errmsg`, `_dist_code`, `_length_code`), not claimed | NonMatching (2026-11-11): 32 of 32 claimed functions at 100 %; not `Matching` while the rest of each file (`static` tables, unused functions) is not claimed |
| `zlib-1.2.5/{adler32,crc32,deflate,inffast,inflate,inftrees,trees,zutil}.c` (`libs/zlib-1.2.5/`, zlib 1.2.5, 4.1 b1049, `--cpu=MPCore`) | 18 `.text` ranges (`config/jpn/splits.txt`), all in 0x006951B4-0x006B0DD0, interleaved with the SDK copy's | the 1.2.5 copy (called from the network code), 30 functions under their analysis names (`fn_<address>`, `libs/zlib-1.2.5/stub/names.h`, `notes/COMPILER.md`); `fn_006951B4` (`build_tree`) has `keep_pool`; data referenced under the `lbl_` names of this copy's tables (`z_errmsg` 0x0076A724, `configuration_table` 0x00748968, `lenfix` 0x007489E0, `order` 0x00749260, `_dist_code` 0x0076A2EC, `_length_code` 0x0076A4EC), not claimed | NonMatching (2026-11-11): 30 of 30 claimed functions at 100 %; not `Matching` while the rest of each file is not claimed |
