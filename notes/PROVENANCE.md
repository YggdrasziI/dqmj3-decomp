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
| `configure.py` | version `jpn` (`CTR-P-BJ3J`); no source objects; progress categories game / sdk / nw / net / unknown; progress image disabled; compiler and flags marked as placeholders |
| `tools/ctr/analyze.py` | after ARM code, a Thumb guess needs a Thumb `push` prologue (`is_thumb_prologue`) |
| `tools/ctr/report_accounting.py` | BigRed's total code size check removed |
| `tools/project.py` | report command chained through `cmd /s /c` on Windows |
| `tools/download_tool.py` | generic User-Agent |
| `tools/ctr/*.py`, `tools/progress_image.py` | `usa` → `jpn` in usage strings |
| `tools/__init__.py`, `decompctx.py`, `ninja_syntax.py`, `tools/ctr/{arm,check,elf,image,link,linker,prelink,split,strpool,symbols,units}.py` | none beyond the line above |
| `notes/BUILD_SYSTEM.md` | from `docs/build_system.md`: NSMB2 facts removed or marked, changes of this project added |
| `.editorconfig`, `.gitattributes`, `.clang-format`, `LICENSE` | none |

## Scripts from DQMJ2

Source: the owner's DQMJ2 decompilation (`YggdrasziI/dqmj2-decomp`, CC0-1.0), commit
`80b83b28a403213e23764af195af92a52b4bd7a9`.

| Our file | Changes |
|---|---|
| `tools/report_diff.py` | dsd gap units (`_dsd_gap@`) replaced by automatic units (`auto/`) |

## Project documents

`SPEC.md`, `notes/`, `.gitignore` follow DQMJ2's (same commit), rewritten for this game
and platform.
