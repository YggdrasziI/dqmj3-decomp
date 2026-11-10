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

No `[[regions]]` from these: no bound is proven.

## String pools (2026-11-10)

armcc 4.1 b921 puts strings that data refers to in mergeable `.conststring` /
`.constwstring` sections (checked by compiling a table of `const char*` and
`const wchar_t*` with the project's flags), and armlink merged each into one pool.
Both are in `config.toml`:

| Pool | Range | Evidence |
|---|---|---|
| `.conststring` | 0x007C1724-0x007C3D2E (0x260A) | the only long run of packed narrow strings that data points to: 319 ASCII strings, no padding, no duplicate, none the tail of another; 319 pointers, one to the start of each string, none from code. One more pointer (0x0082061C) points to the `r` that ends a string: of the 7 strings ending in `r`, armlink's rule (the last when read backwards, `tools/ctr/strpool.py`) picks `dmp_LightEnv.shadowSelector`, the one pointed to. |
| `.constwstring` | 0x007CAB34-0x007CC0A2 (0x156E) | 168 UTF-16 strings (`rom:/data/Community/CommunityPrize.nut`, ...), packed, no duplicate, none the tail of another, each pointed to once at its start (167 from data, 1 from `.text`); 0xFF padding (armlink's fill) right before and after, so one section of its own. |

Other strings in `.rodata` are 4-aligned with zero padding between them (compiler
`.constdata`), or in small sections that 0xFF padding separates (for example many
UTF-16 `rom:/data/...` paths at 0x007C4490-0x007C6900, one section each). The pools
are not proven by a matched unit yet.

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
- armlink is not in decomp.me's `armcc.zip`, so the sort options (`--sort=...`) can
  not be tried. Open.

## Units

| Unit | Range | Content | Status |
|---|---|---|---|
| `game/FieldScriptFunc.cpp` | `.text` 0x002546FC-0x00254784, `.rodata` 0x00725800-0x0072580F | `SetFogDensity_` and its `__FUNCTION__` string | Matching (2026-11-10) |
| `squirrel/<file>.cpp` (11 files, `libs/squirrel/`) | 128 `.text` ranges | the 224 functions found by the sweep, each claimed by the file the sweep compiled it from | NonMatching: 217 of 224 at 100 % in objdiff with relocation targets compared; the 7 others refer to long string literals (`.constdata`), whose `.rodata` ranges are not claimed yet; the rest of each file differs from the game or is not located yet |
