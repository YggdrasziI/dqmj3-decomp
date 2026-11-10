# Splits and region map

How `.text`, `.rodata` and `.data` divide into libraries and units, with the evidence
for every boundary. A boundary is a hypothesis until a unit on each side matches.

## Current state

- `config/jpn/splits.txt` claims one unit; every other byte belongs to an automatic
  unit (`auto/<section>_<address>`, 64 KiB grid, see `notes/BUILD_SYSTEM.md`).
- `config/jpn/symbols.txt` comes from `tools/ctr/analyze.py` (2026-11-10): 34,058
  functions (332 Thumb), 14,995 data labels. 127 functions have control flow the
  analysis could not follow; their bounds are not trusted.
- No `[[regions]]` and no string pools in `config/jpn/config.toml` yet.

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

## Units

| Unit | Range | Content | Status |
|---|---|---|---|
| `game/FieldScriptFunc.cpp` | `.text` 0x002546FC-0x00254784, `.rodata` 0x00725800-0x0072580F | `SetFogDensity_` and its `__FUNCTION__` string | Matching (2026-11-10) |
| `squirrel/<file>.cpp` (11 files, `libs/squirrel/`) | 128 `.text` ranges | the 224 functions found by the sweep, each claimed by the file the sweep compiled it from | NonMatching: 217 of 224 at 100 % in objdiff with relocation targets compared; the 7 others refer to long string literals (`.constdata`), whose `.rodata` ranges are not claimed yet; the rest of each file differs from the game or is not located yet |
