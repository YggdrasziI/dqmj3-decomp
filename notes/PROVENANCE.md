# Provenance of reused code

Every file or function taken from another project, with the project, its commit, its
license and the changes made.

## Build system (`configure.py`, `tools/`)

Source: [T3CHNOLOG1C/BigRed](https://github.com/T3CHNOLOG1C/BigRed) (New Super Mario
Bros. 2 decompilation, **CC0-1.0**), commit `3236a656edbb8c6f353b53779445fed18c9cb4df`,
copied on 2026-11-10. `tools/ninja_syntax.py` is from the Ninja project (Copyright 2011
Google Inc., **Apache-2.0**, notice kept, license in `LICENSES/Apache-2.0.txt`).

| Our file | Changes |
|---|---|
| `configure.py` | version `jpn` (`CTR-P-BJ3J`); own objects and libraries (`game`, `squirrel`); progress categories game / sdk / nw / net / lib / unknown; progress image disabled; compiler and flags marked as placeholders |
| `tools/ctr/analyze.py` | after ARM code, a Thumb guess needs a Thumb `push` prologue (`is_thumb_prologue`) |
| `tools/ctr/report_accounting.py` | BigRed's total code size check removed; data objects in `.text` counted for their size |
| `tools/project.py` | report command chained through `cmd /s /c` on Windows; report generated with `functionRelocDiffs=name_address`; armcc started with a native path on Windows |
| `tools/ctr/linker.py` | data sections with only unknown local symbols (`__FUNCTION__`) placed like sections without symbols; the literal lookup of `locate_string` moved to `StringPool.literal_containing`; calls to the functions in `inlined_functions` of `config.toml` replaced by their instruction, their compiled body checked (`inline_body` split out of `inline_call`); an instruction of `bx lr` is an empty function, inlined as `mov r0, r0` |
| `tools/ctr/arm.py` | a function is walked again when a word was decoded as code before being found as literal pool data |
| `tools/ctr/image.py` | `inlined_functions` in `config.toml` |
| `tools/ctr/split.py`, `tools/ctr/image.py` | `[init_array]` in `config.toml`: the static initializer table is split into `.init_array` sections with `R_ARM_TARGET1` relocations; `split.py`: a pointer is a string reference only when `StringPool.locate` gives back its address |
| `tools/ctr/split.py` | the attribute `keep_pool` of `symbols.txt` keeps a trailing LDR-only pool in a function's size |
| `tools/ctr/link.py` | `parse_intermixed_args` (Python 3.12 left the units after the options unparsed) |
| `tools/ctr/prelink.py` | drops `R_ARM_NONE` relocations; renames template sections `t.<name>` to `i.<name>`; rewrites the addends of string pointers in data to the layout of split objects |
| `tools/ctr/strpool.py` | padding (zero, 0xFF) between strings skipped; a pointer to a terminator is the empty string; `literal_containing` |
| `tools/download_tool.py` | generic User-Agent |
| `tools/ctr/*.py`, `tools/progress_image.py` | `usa` → `jpn` in usage strings |
| `tools/__init__.py`, `decompctx.py`, `ninja_syntax.py`, `tools/ctr/{check,elf,symbols,units}.py` | none beyond the line above |
| `notes/BUILD_SYSTEM.md` | from `docs/build_system.md`: NSMB2 facts removed or marked, changes of this project added |
| `.editorconfig`, `.gitattributes`, `.clang-format`, `LICENSE` | none |

## Squirrel 2.2.5

Source: the public release `squirrel_2.2.5_stable.tar.gz` (SourceForge, SHA-1
`a3d36da3ca4da5897df4d9ef93cc65ae09f1e3b4`), Copyright (c) 2003-2011 Alberto
Demichelis, **zlib license** (`libs/squirrel/COPYRIGHT`, copy in
`LICENSES/Zlib-Squirrel.txt`). Copied on 2026-11-10 with the owner's approval.

| Our files | Changes |
|---|---|
| `libs/squirrel/include/squirrel.h`, `libs/squirrel/squirrel/*.{cpp,h}` | none (line endings normalized by git), except: |
| `libs/squirrel/squirrel/sqobject.cpp` | altered (notice at the top): `SQArray::Extend` takes each element through a local reference (2026-11-10) |
| `libs/squirrel/squirrel/sqarray.h` | altered (notice at the top): `SQArray::ShrinkIfNeeded` reads the capacity into a local (2026-11-10) |

## zlib 1.2.7

Source: [madler/zlib](https://github.com/madler/zlib) tag `v1.2.7` (commit
`30a1c7065dc1dc2c2ed68ed403792b660bfdd805`, GitHub archive `v1.2.7.tar.gz` SHA-1
`0e88ec14f594dec94b6dff66c2eddf5aae376d13`), Copyright (C) 1995-2012 Jean-loup Gailly and
Mark Adler, **zlib license** (`libs/zlib/README`, copy in `LICENSES/Zlib-zlib.txt`). Copied
on 2026-11-11 with the owner's approval: the library files of the release root
(`*.c` and `*.h` without the `gz*` files, `README`); `gzguts.h` added on the same day
(`zutil.c` includes it without `Z_SOLO`).

| Our files | Changes |
|---|---|
| `libs/zlib/*.{c,h}`, `libs/zlib/README` | none, except: |
| `libs/zlib/stub/{fcntl.h,sys/types.h}` | our own empty headers, not zlib's: armcc 4.1 has neither (2026-11-11); `zconf.h` is unaltered again |
| `libs/zlib/inflate.c`, `libs/zlib/deflate.c` | altered (notice at the top): `inflateInit2_` and `deflateInit2_` first call `fn_inline_00104C54(0, 0x0400028B)` (a name of this project's convention) (2026-11-11) |

## zlib 1.2.5

Source: [madler/zlib](https://github.com/madler/zlib) tag `v1.2.5` (tag object
`41fd7e507609681a7ae9e641363b0fed60ea708b`, commit
`9712272c78b9d9c93746d9c8e156a3728c65ca72`, GitHub archive `v1.2.5.tar.gz` SHA-1
`a4e8adc8bd7d920ffa79e25c823e2b906894a61f`), Copyright (C) 1995-2010 Jean-loup Gailly and
Mark Adler, **zlib license** (`libs/zlib-1.2.5/README`, same terms as
`LICENSES/Zlib-zlib.txt`). Copied on 2026-11-11 with the owner's approval: the library
files of the release root (`*.c` and `*.h` without the `gz*` files, `README`).

| Our files | Changes |
|---|---|
| `libs/zlib-1.2.5/*.{c,h}`, `libs/zlib-1.2.5/README` | none |
| `libs/zlib-1.2.5/stub/names.h` | our own header, not zlib's: `#define`s from zlib names to this copy's analysis names, passed with `--preinclude` (2026-11-11) |

## Scripts from DQMJ2

Source: the owner's DQMJ2 decompilation (`YggdrasziI/dqmj2-decomp`, CC0-1.0), commit
`80b83b28a403213e23764af195af92a52b4bd7a9`.

| Our file | Changes |
|---|---|
| `tools/report_diff.py` | dsd gap units (`_dsd_gap@`) replaced by automatic units (`auto/`) |
| `tools/progress_badges.py` | regions, modules and overlays replaced by the progress categories of the report; default report `build/<version>/tracker/report.json` |
| `tools/compiler_sweep.py` | rewritten for armcc and `code.bin` (same purpose as DQMJ2's, which drove mwccarm); reads another project's objects and flags through its `configure.py` |
| `tools/asm_compare.py` | objdiff-cli from `build/tools/`; examples and wording for this project's units (`auto/` instead of dsd delinks); the objdiff call split into helpers shared with `why_diff.py` |
| `tools/why_diff.py` | `--trace` (mwccarm coloring trace through `tools/mwcc_sched.py`) removed; `--objects` added; VFP registers (`sN`, `dN`) counted as registers; `add rN, pc, #imm` counted as a literal pool offset; the kinds marked as carried over from mwccarm |
| `tools/unit_candidates.py` | rewritten for `code.bin`: functions outside every `splits.txt` range, calls from the relocations of the split objects; modules, overlays and fixed game regions removed; optional `--region` from `config.toml` |
| `tools/permute.py` | armcc instead of mwccarm, with the unit's command from `build.ninja`; variants prelinked (`tools/ctr/prelink.py`) and compared with `build/<version>/delink/`; the word scorer reads objects with `tools/ctr/elf.py`; the `__typeof__` mutations removed (armcc rejects `__typeof__` with this project's flags); loop counters use `unsigned int` instead of `u32`; finds methods defined in their class body |

## Own scripts

| File | Purpose |
|---|---|
| `tools/disasm.py` | disassembly of functions of the original image, through objdiff-cli |
| `tools/ghidra_elf.py` | writes `code.bin` as an ELF executable (segments from `config.toml`) for Ghidra |
| `tools/ghidra_sync.py`, `tools/ghidra/SyncSymbols.java` | import into a Ghidra project and apply `symbols.txt` (Thumb mode, functions, labels, names) headless; same purpose as DQMJ2's `ghidra_sync.py`, which drove dsd-ghidra |
| `tools/link_density.py` | call-graph density of `.text` windows, to find self-contained (library) blocks |
| `tools/reloc_names.py` | names the analysis symbols that matched functions call or refer to, from the relocations of our objects |
| `tools/sweep_names.py` | names `symbols.txt` functions from a `compiler_sweep.py --json` result |

## Project documents

`SPEC.md`, `notes/`, `.gitignore` follow DQMJ2's (same commit), rewritten for this game
and platform.
