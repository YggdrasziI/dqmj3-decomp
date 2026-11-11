# Dragon Quest Monsters: Joker 3 (3DS) decompilation — specification

## Goal

Rebuild the program of Dragon Quest Monsters: Joker 3 (Nintendo 3DS, Japan) from C/C++
source written from scratch so that, compiled with the original compiler and flags, it
produces a `code.bin` (the decompressed ExeFS `.code`) identical byte for byte to the
original.

Out of scope: a port, game assets (RomFS), any redistribution of game files, rebuilding
the `.3ds` image itself (ExeFS compression, NCCH/NCSD headers, RomFS). Those may be
targeted later, on the owner's request.

## Target image

| Item | Value | Evidence |
|---|---|---|
| Product code | `CTR-P-BJ3J` (Japan) | NCCH header 0x150 (`ctrtool`) |
| Title ID | `000400000016AD00` | NCCH header 0x118 |
| Internal name | `break` | exheader 0x000 (`ctrtool`: "Name: break") |
| Title version | 0.3.0 (v48) in the card's mastering metadata; remaster version 0 | `ctrtool` output |
| `.3ds` SHA-1 | `ad4b2ec453ca426150ea4f3990257e0f38f9bd06` (1 GiB, decrypted: NCCH flags[7] = 0x04 NoCrypto) | `Get-FileHash` |
| exheader SHA-1 | `dd5ad9e5bce006492aa449837f8b2a2594bfdee0` | `extract/jpn/exheader.bin` |
| `code.bin` SHA-1 | `0d9795cacac26c967390f02355dc409132227553` (7,487,488 bytes, decompressed) | `config/jpn/config.toml` |
| `.text` | 0x00100000, 0x61E34C bytes (0x61F pages) | exheader |
| `.rodata` | 0x0071F000, 0xAF2DC bytes (0xB0 pages) | exheader |
| `.data` | 0x007CF000, 0x54EAC bytes (0x55 pages) | exheader |
| `.bss` | 0x00823EAC (after `.data`), 0x25504 bytes | exheader |
| Stack | 0x40000 bytes | exheader |
| System mode | prod (64 MB); New 3DS: snake prod (124 MB) | exheader |
| Functions | 34,058 found by `tools/ctr/analyze.py` (332 Thumb), 127 with control flow it could not follow | `config/jpn/symbols.txt` |
| Code size | 6,310,790 bytes measured by objdiff over all functions | `build/jpn/report.json` |

### Libraries seen in the image

From strings in `code.bin` (addresses still to be recorded in `notes/COMPILER.md`).
Each is a lead for the region map, not yet an attribution:

- **CTR-SDK** (`nn::`): `nn::ac`, `nn::friends`, `nn::http`, ... (error strings such as
  `nn::ac::Initialize() failed`).
- **zlib**, two copies: the SDK's (version string `1.2.7.f-NINTENDO-CTR-SDK-v1`,
  `libs/zlib/` from the public 1.2.7) and a zlib 1.2.5 called from the network code
  (`libs/zlib-1.2.5/`, compiled under its analysis names, `notes/COMPILER.md`).
- **NEX** (`nn::nex`, online services) and **PIA** (`NN_PIA_SESSION_...`, peer-to-peer
  sessions).
- **NintendoWare for CTR**: file names `.bflim` (layout images), `.bffnt` (fonts), and
  `Eft_Ptcl_*.vsh` (effect shaders).
- **Squirrel 2.2.5** (scripting): version string `Squirrel 2.2.5 stable` at
  0x00155C40; 244 functions match the public source (`notes/COMPILER.md`).
- **Square Enix** online library: URLs `wi-fi.infralib.square-enix.com`,
  `dqmj3ds.sil2.square-enix.com`, `SIL_ERR_*` and `X-Sil-Version`.
- Game code: the Squirrel bindings pass their file name to the error path:
  `BattleScriptFunc.cpp` (140 functions in 0x0012D8E0-0x00148AE0) and
  `FieldScriptFunc.cpp` (186 functions in 0x00251FE8-0x0025D13C).

## Other versions

| Release | Product code | Status |
|---|---|---|
| Dragon Quest Monsters: Joker 3 (Japan) | `CTR-P-BJ3J` | this project, reference version |
| Dragon Quest Monsters: Joker 3 Professional (Japan) | `CTR-P-BDQJ` | separate game and project (`DQMJ3P-decomp`), later, on the owner's request |

Updates (patch titles) are out of scope until the owner decides otherwise.

## Toolchain

Evidence and the candidate analysis go in `notes/COMPILER.md`. How the build works:
`notes/BUILD_SYSTEM.md`.

- **Compiler:** RVCT 4.1 build 921 (`armcc`), flags `--cpp --arm --cpu=MPCore
  --fpmode=fast --apcs=/interwork --split_sections -O3 -Otime --no_rtti --no_rtti_data
  --signed_chars`. Identified among the 14 builds of decomp.me's `armcc.zip` by
  compiling Squirrel 2.2.5 and zlib 1.2.7 (`notes/COMPILER.md`).
- **No armlink:** the original linker is not available. `tools/ctr/` (after BigRed)
  splits the original image into one relocatable object per unit, and links compiled
  objects back at the addresses of `symbols.txt`, reproducing what armlink did to the
  code (`notes/BUILD_SYSTEM.md`).
- **objdiff-cli v3.8.2**: per-unit diff and the progress report.
- **Python 3.11+** (`tomllib`) and **ninja**. No other package is required.
- Optional: Ghidra 12.2 (ARM v6 little-endian, an ELF made from `code.bin`), outside
  the repository (`notes/GHIDRA.md`).

## Acceptance criteria

- Every build ends with `build\jpn\code.bin: OK` (`ninja`): the linked image has the
  SHA-1 of `config/jpn/config.toml`.
- A unit is `Matching` in `configure.py` only when objdiff reports 100 % for all its
  functions and data and the build still matches. Anything else stays `NonMatching`,
  with the remaining gap written above each unfinished function.
- A split that builds proves the bytes, not the translation unit: a unit boundary is
  proven only once the unit is decompiled and matches (`notes/SPLITS.md`).
- Every name, compiler fact or structure layout rests on evidence (strings with their
  address, library signatures, symbols of another project on the same library, an
  objdiff diff, a build result). Without evidence it is labelled a hypothesis. Names
  given in Ghidra, or found in another Dragon Quest decompilation, are not evidence by
  themselves.
- Reused code from another project is logged with its commit and license in
  `notes/PROVENANCE.md`.

## Naming conventions

- Analysis names stay until proven: `fn_<addr>` (functions), `lbl_<addr>` (data),
  `__ctr_start` (entry point).
- Game units: `src/game/unit_<start address>.cpp` while real file names are unknown.
  A unit takes a real file name when its code passes that name (the script bindings'
  error path passes `FieldScriptFunc.cpp` or `BattleScriptFunc.cpp`).
- Function names from `__FUNCTION__`: when a function passes its own `__FUNCTION__`
  string, that string is its name (`SetFogDensity_`).
- Unknown classes and structs: `Unk<Name>` or `Unk<address>`; unknown methods keep the
  address (`fn_<addr>`, mangled as a member when the class is known).
- A function with no body in the image (armlink inlined every call and removed it):
  `fn_inline_<address of its first call site>`, listed in `inlined_functions` of
  `config.toml`. This is a convention of this project, not evidence of anything:
  replace it when the real name is proven. In use: `fn_inline_00104C54`
  (`notes/COMPILER.md`).
- Library code under `libs/<lib>/{include,src}` (`nn`, `nw`, `rvct`, `zlib`, `nex`,
  `pia`, ...; each library sets its `src_dir` in `configure.py`; a public source copied
  as is keeps its own layout, as `libs/squirrel/{include,squirrel}`, `libs/zlib/` and `libs/zlib-1.2.5/`), with the library's
  real names once identified by signature or a reference project. Starting point for
  `nn::`: zeldaret/3ds_sdk (CC0).
- A unit's name in `splits.txt` is its source path relative to that `src_dir`
  (`game/unit_00123456.cpp` for `src/game/unit_00123456.cpp`).
- Code, comments, notes and commit messages are in English.

## Layout

```
README.md SPEC.md LICENSE LICENSES/   CC0-1.0; Apache-2.0 for tools/ninja_syntax.py;
                                      zlib for libs/squirrel/, libs/zlib/ and
                                      libs/zlib-1.2.5/
                                      (notes/PROVENANCE.md)
configure.py                          project description, generates build.ninja
config/jpn/                           config.toml, symbols.txt, splits.txt
orig/jpn/code.bin                     decompressed .code of the user's dump (git-ignored)
extract/jpn/                          ctrtool output: exheader, ExeFS, RomFS (git-ignored)
build/                                build output (git-ignored)
src/  include/  libs/                 sources and headers
tools/                                tools/ctr/ (split, link, check, analysis), scripts
progress/jpn/                         progress badges and history
notes/                                reference documentation
.github/workflows/                    CI: build and check code.bin in a private image
```

## Build

```
python configure.py   # generate build.ninja
ninja                 # compile, link, check code.bin, split, objdiff report
```

Put the decompressed code at `orig/jpn/code.bin`:
`ctrtool -n 0 --exefsdir=extract/jpn/exefs --decompresscode <dump>.3ds`, then copy
`extract/jpn/exefs/code.bin`. Useful targets: `ninja check` (stop after the image
check), `ninja split`. On Windows use native tools, not WSL.
