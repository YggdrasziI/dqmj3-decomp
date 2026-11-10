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
code around it. What delimits a run is not known (hypotheses: an armlink `--sort`
within groups of input sections, or partial links sorted one by one). The 26 run
bounds are only where two known names are out of order, not proven unit bounds.

## Units

| Unit | Range | Content | Status |
|---|---|---|---|
| `game/FieldScriptFunc.cpp` | `.text` 0x002546FC-0x00254784, `.rodata` 0x00725800-0x0072580F | `SetFogDensity_` and its `__FUNCTION__` string | Matching (2026-11-10) |
| `squirrel/<file>.cpp` (11 files, `libs/squirrel/`) | 128 `.text` ranges | the 224 functions found by the sweep, each claimed by the file the sweep compiled it from | NonMatching: 217 of 224 at 100 % in objdiff with relocation targets compared; the 7 others refer to long string literals (`.constdata`), whose `.rodata` ranges are not claimed yet; the rest of each file differs from the game or is not located yet |
