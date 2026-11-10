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
| `tools/ctr/report_accounting.py` | BigRed's total code size check removed |
| `tools/project.py` | report command chained through `cmd /s /c` on Windows; report generated with `functionRelocDiffs=name_address`; armcc started with a native path on Windows |
| `tools/ctr/linker.py` | data sections with only unknown local symbols (`__FUNCTION__`) placed like sections without symbols |
| `tools/ctr/link.py` | `parse_intermixed_args` (Python 3.12 left the units after the options unparsed) |
| `tools/ctr/prelink.py` | drops `R_ARM_NONE` relocations; renames template sections `t.<name>` to `i.<name>` |
| `tools/download_tool.py` | generic User-Agent |
| `tools/ctr/*.py`, `tools/progress_image.py` | `usa` → `jpn` in usage strings |
| `tools/__init__.py`, `decompctx.py`, `ninja_syntax.py`, `tools/ctr/{arm,check,elf,image,split,strpool,symbols,units}.py` | none beyond the line above |
| `notes/BUILD_SYSTEM.md` | from `docs/build_system.md`: NSMB2 facts removed or marked, changes of this project added |
| `.editorconfig`, `.gitattributes`, `.clang-format`, `LICENSE` | none |

## Squirrel 2.2.5

Source: the public release `squirrel_2.2.5_stable.tar.gz` (SourceForge, SHA-1
`a3d36da3ca4da5897df4d9ef93cc65ae09f1e3b4`), Copyright (c) 2003-2011 Alberto
Demichelis, **zlib license** (`libs/squirrel/COPYRIGHT`, copy in
`LICENSES/Zlib-Squirrel.txt`). Copied on 2026-11-10 with the owner's approval.

| Our files | Changes |
|---|---|
| `libs/squirrel/include/squirrel.h`, `libs/squirrel/squirrel/*.{cpp,h}` | none (line endings normalized by git) |

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
| `tools/permute.py` | armcc instead of mwccarm, with the unit's command from `build.ninja`; variants prelinked (`tools/ctr/prelink.py`) and compared with `build/<version>/delink/`; the word scorer reads objects with `tools/ctr/elf.py`; the `__typeof__` mutations removed (armcc rejects `__typeof__` with this project's flags); loop counters use `unsigned int` instead of `u32` |

## Own scripts

| File | Purpose |
|---|---|
| `tools/disasm.py` | disassembly of functions of the original image, through objdiff-cli |
| `tools/reloc_names.py` | names the analysis symbols that matched functions call or refer to, from the relocations of our objects |
| `tools/sweep_names.py` | names `symbols.txt` functions from a `compiler_sweep.py --json` result |

## Project documents

`SPEC.md`, `notes/`, `.gitignore` follow DQMJ2's (same commit), rewritten for this game
and platform.
