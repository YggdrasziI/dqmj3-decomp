# References

Projects and tools used, and what may be taken from each. Reusing code needs a known
license (CC0 and Unlicense are approved); anything else needs the owner's approval
first. Every reuse is logged in `notes/PROVENANCE.md`.

## 3DS decompilations

- [T3CHNOLOG1C/BigRed](https://github.com/T3CHNOLOG1C/BigRed) (New Super Mario Bros. 2,
  **CC0**): build system, `tools/ctr/` (split, prelink, link, check, analysis), RVCT 4.1
  flags, armlink behaviour. Base of this project. Also has sead, PIA and `nn::os`
  sources: references for library units once this game's compiler is known.
- [zeldaret/oot3d](https://github.com/zeldaret/oot3d) (Ocarina of Time 3D, **CC0**):
  RVCT 4.0 b821, real armlink with a scatter file (`disassembly/oot3d.cfg`),
  `exefs2elf.py` (code.bin to ELF), `n3dsdisasm`, `ctrtool` binaries.
- [zeldaret/3ds_sdk](https://github.com/zeldaret/3ds_sdk) (**CC0**): a rebuild of
  CTR-SDK `nn::` headers and sources (applet, fs, gx, hid, os, snd, srv, svc, ...).
- acnl-decomp (Animal Crossing: New Leaf): GCC build, not byte-matching. Reference for
  names only, never evidence.
- mh4u-decomp (Monster Hunter 4 Ultimate): no code yet.
- [mooki000/kanken-training-2-decomp](https://github.com/mooki000/kanken-training-2-decomp)
  (Kanken Training 2, `CTR-P-B2KJ`, armcc matching decompilation, **GPL-3.0**): read only,
  as an example; no code taken. Has the same CTR-SDK call `f(0, 0x0400xxxx)` to an empty
  function inlined by armlink (`func_0014f7e8`, no real name either).

- [3dsdecomp](https://github.com/3dsdecomp) (read only, no code taken):
  [RedPepper](https://github.com/3dsdecomp/RedPepper) (Super Mario 3D Land EU, armcc
  matching decompilation, **GPL-3.0**): compiler and armlink flags (`CMakeLists.txt`,
  `notes/COMPILER.md`), and `Symbols/lib/armlib/c_4.l/*.sym`, RVCT C library functions
  listed by library object (`strcmp`, `strstr`, `__printf`, `_printf_*`, ...): leads for
  the C-library regions. `nnsdk` (6 CTR-SDK files: `dbg`, `fs`, `math`, `srv`, `svc`),
  `sead` (6 files), `LibMessageStudio` (MSBT; not in this game: no `MsgStdBn`) and
  `RedPepper-Headers` have **no license**. Their SDK is older (2011) than this game's.
  Names from them are leads only.

## Tools

- [3DSGuy/Project_CTR](https://github.com/3DSGuy/Project_CTR) `ctrtool` v1.2.1:
  extracts the exheader, ExeFS (with `--decompresscode`) and RomFS.
- [decompme/compilers](https://github.com/decompme/compilers) `armcc.zip`: RVCT 4.0,
  4.1 and 5.04 builds (downloaded by `ninja`).
- [encounter/objdiff](https://github.com/encounter/objdiff) v3.8.2: diff and report.
- [decompals/wibo](https://github.com/decompals/wibo): runs armcc on Linux (CI).
- [decomp.me](https://decomp.me): scratches with the `armcc_*` presets.
- Ghidra 12.2 (ARM processor module, ARM v6 little-endian), no 3DS loader: the image is
  loaded as an ELF made with oot3d's `exefs2elf.py`.

## Emulators (source only)

- Azahar (fork of Citra, **GPL-2.0**): read only, no code taken. GDB stub and RPC server
  for dynamic analysis, if needed later.

## Public library sources

- zlib 1.2.7 (zlib license, [madler/zlib](https://github.com/madler/zlib) tag
  `v1.2.7`): the CTR-SDK copy of zlib in the image (`1.2.7.f-NINTENDO-CTR-SDK-v1`, which
  may differ from the public release). Copied into `libs/zlib/` (approved by the owner,
  2026-11-11). zlib 1.2.5 (tag `v1.2.5`, same license): the image's second copy, copied into
  `libs/zlib-1.2.5/` (approved by the owner, 2026-11-11, `notes/COMPILER.md`).
- Squirrel 2.2.5 stable (zlib license, `squirrel_2.2.5_stable.tar.gz` from
  [SourceForge](https://sourceforge.net/projects/squirrel/files/squirrel2/)): the
  game's scripting language. Copied into `libs/squirrel/` (approved by the owner for
  Squirrel, zlib 1.2.7 and zlib 1.2.5 only; other zlib-licensed code still needs approval). Used for the compiler
  sweep.
