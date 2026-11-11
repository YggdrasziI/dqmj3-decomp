# Compiler, SDK and runtime

What is known about how `code.bin` was built, with the evidence for each point.
Anything without evidence is marked as a hypothesis.

## Summary

| Item | Value | Status |
|---|---|---|
| Compiler (Squirrel, built with the game) | RVCT 4.1 build 921 (`armcc`) | proven among the 14 builds of decomp.me's `armcc.zip` (Squirrel sweep) |
| Compiler (script bindings) | ARM Compiler 5.04 b82 | proven against b921 on the script binding units (below); the only 5.x build in the archive, so a nearby 5.x build is not ruled out |
| Compiler (CTR-SDK zlib) | RVCT 4.1 build 1049, 1440 or 1454, `--cpu=MPCoreNoVFP`, `-O3 -Otime`, C90 | proven (zlib sweep); the three builds are not told apart |
| Optimisation | `-O3 -Otime` | proven (Squirrel, zlib) |
| `--fpmode=fast`, `--signed_chars` | yes | proven (Squirrel) |
| `--cpu=MPCore --arm --apcs=/interwork --split_sections --no_rtti_data` | used | consistent with every match; not tested one by one |
| `--no_rtti` | — | makes no difference so far |
| `--no_dep_name` | — | only needed to compile the public Squirrel source (template lookup); no effect on code |

Builds compared: RVCT 4.0 b771, b821, b865, b902; RVCT 4.1 b561, b713, b791, b844, b894,
b921, b1049, b1440, b1454; ARM Compiler 5.04 b82. A build not in that archive (for
example 4.1 builds between 921 and 1049) cannot be ruled out.

## Evidence

Sweeps by `tools/compiler_sweep.py` (2026-11-10): reference sources are compiled with
each build, relocated words are masked, and each function is searched for in `.text`.
A function counts when it is found at exactly one address. Masking: the 24-bit offset
of ARM `bl`/`b` (condition and opcode kept), both halves of a Thumb `bl`, and every
word with a data relocation.

### Squirrel 2.2.5 (compiled with the game)

`"Squirrel 2.2.5 stable"` at 0x001557C0. Source: the 2.2.5 stable release
(`squirrel_2.2.5_stable.tar.gz`, zlib license), the 11 files of `squirrel/`, flags of
`configure.py` plus `--no_dep_name`. 385 functions compiled (383 with b921).

| Build | Functions found |
|---|---|
| 4.0 b771, b821, b865 | 31 |
| 4.0 b902, 4.1 b561 | 32 |
| 4.1 b713 | 201 |
| 4.1 b791 | 217 |
| 4.1 b844 | 220 |
| 4.1 b894 | 218 |
| **4.1 b921** | **224** |
| 4.1 b1049, b1440, b1454 | 221 (the same 221) |
| 5.04 b82 | 71 |

Build 921 finds every function the other 4.1 builds find. Outside 4.1, three functions
are found that b921 does not find at a single address: `weakref_ref` and
`closure_bindenv` (28 bytes each, both at 0x001B098C with 4.0: identical small code,
ambiguous with b921), and `__sti___11_sqstate_cpp__null_` (the static initializer of
`sqstate.cpp`, 192 bytes at 0x00655B48, 5.04 only; open question). What rules the
other builds out:

- found with b921 but not b1049 / b1440 / b1454: `SQFunctionProto::Load` (0x002694FC,
  9644 bytes), `SQCompiler::CompExp` (0x0019D620, 540 bytes),
  `SQCompiler::BitwiseAndExp` (0x001C174C, 192 bytes);
- found with b921 but not b894 (6): `SQVM::ARITH_OP` (0x0019774C, 952 bytes, b921 and
  later only), `SQVM::FallBackGet` (0x0018DEFC, 1224 bytes),
  `SQFuncState::AddInstruction` (0x0019DB7C, 876 bytes), `CompExp`, `IdType2Name`,
  `SQSharedState::MarkObject`;
- every function found by another 4.1 build or by 5.04 is also found by b921.

An earlier version of the sweep masked whole branch words; it counted 244 functions
with b921 and some false positives (a `b` taken for a `bl`), now gone.

Flags, with b921 (functions found): base flags 224; `-O3 -Ospace` 30; `-O2 -Otime` 51;
without `--fpmode=fast` 223; without `--signed_chars` 219; without `--no_rtti` 224.

The 224 functions cover 88,592 bytes; 12 more are found at several addresses (small
identical bodies). 222 of the 224 are named in `symbols.txt` by `tools/sweep_names.py`
(the other two already had their name). The rest
differ (game changes to Squirrel, inlining across files, or code the linker removed) and
are not analysed yet.

### zlib: two copies (2026-11-11)

The image links **two zlib copies**, whose functions are interleaved by the name sort of
0x00694000-0x006B2000. The first sweep (zlib 1.2.7 with `-DZ_SOLO`, 11 functions) mixed
them; functions that are the same in 1.2.5 and 1.2.7 can only be told apart by their
calls. Calls (`BL`, `B` and function pointers in literal pools) inside that window form
two components with no link between them:

- **CTR-SDK zlib 1.2.7** (`1.2.7.f-NINTENDO-CTR-SDK-v1`, 5 copies of the string: inline
  at 0x0047AFF4, 0x0047C1D8, 0x0056C0B4 and in `.rodata` at 0x0073667C, 0x00736698).
  The functions that pass that string (0x003E1538, 0x003E1604, 0x0047AEF8, 0x0047C14C,
  0x0056BFD4, 0x0056C0D0) call this copy. Its exported functions start with a `mov r0,
  r0` word that callers branch to (0x0069D0C8, 0x0069D1C8, 0x0069D6BC, 0x0069F088,
  0x0069F0D8, 0x0069F240). Its `inflateInit2_` (0x0069F0DC) and `deflateInit2_`
  (0x0069D2AC) point to an 8-byte default allocator, `mul r0, r1, r2; b fn_002FE59C`
  (0x006A0010): `zcalloc` of 1.2.7 built **without** `Z_SOLO` (with `Z_SOLO` there is no
  default allocator).

  It was built with its own compiler and CPU (a prebuilt SDK library):
  - `--cpu`: with `MPCore` (the game's) only the functions that do not depend on it
    match. `6`, `6K`, `6Z` and `ARM1136J-S` match 15 functions, with the copy's register
    choices but without the `nop` (0xE320F000) the copy has, for example between `subs`
    and `beq` in `updatewindow`. `MPCoreNoVFP` (same as `MPCore.no_vfp`) matches
    everything: MPCore scheduling and its `nop`s, and the other register choices.
    `ARM1136J-S-rev1`, `ARM1136JF-S-rev1`, `ARM1176JZF-S` and `6T2` match less. A `mov r0,
    r0` (0xE1A00000) is not one of these `nop`s: it is a call armlink inlined
    (`notes/BUILD_SYSTEM.md`). The game's code has 0xE320F000 too (28,538 words in 6,326
    functions), from `MPCore`.
  - Build, with `--cpu=MPCoreNoVFP`: `deflate` matches with 4.1 b1049, b1440 and b1454
    only; `inflate_table` with b791, b844, b1049, b1440, b1454 but not b894 or b921.
    1049, 1440 and 1454 find the same 20 functions.

  Source: zlib 1.2.7, no `Z_SOLO`, `--c90`; armcc 4.1 has no `<sys/types.h>` (included
  by `zconf.h`) or `<fcntl.h>` (by `gzguts.h`, which `zutil.c` includes without
  `Z_SOLO`), so `libs/zlib/stub/` has empty ones. With b1049 and `--cpu=MPCoreNoVFP`, 32
  functions of the copy are at 100 % (`notes/SPLITS.md`), with `zcalloc` and `zcfree`
  (named from the references of `deflateInit2_`), whose calls named `malloc`
  (0x002FE59C) and `free` (0x00301A1C). `inflateInit2_` and `deflateInit2_` each start with an
  added call `f(0, 0x0400028B)` to an empty function that armlink inlined (`mov r0, #0;
  ldr r1, =0x0400028B; mov r0, r0`). The same call, with another constant
  (0x04000000-0x0400029A, each used once), starts 21 other functions of SDK and network
  code (first at 0x00104C54 in `fn_00104C48`; 0x00113450 near the `fs:USER` client,
  0x0017FA48, the `ir:USER` client...): likely a library-use marker of the CTR-SDK
  (hypothesis; Kanken Training 2 has the same pattern, `notes/REFERENCES.md`). Every site
  is ARM and inlined, so no call shows the function, and no reference project names it.
  The two zlib functions call it as `fn_inline_00104C54`, **a name of this project's
  convention, not evidence** (`SPEC.md`), listed in `inlined_functions` of `config.toml`
  as an empty function; the source change is marked `DQMJ3` in `libs/zlib/inflate.c`
  and `deflate.c`. That every site calls the same function is a hypothesis too.
- **zlib 1.2.5**: called from the network block (0x0040F940, which refers to the string
  `1.2.5` at 0x0073C75C, calls `deflateInit2_` 0x006A3248). The public 1.2.5 source,
  unaltered, with `--cpu=MPCore` (the game's CPU, not the SDK copy's `MPCoreNoVFP`) and
  `--c90`, finds 20 functions with build 921, 22 with 1049, 1440 and 1454, 19 with 894;
  with 1049 all 30 functions of the copy are at 100 % (2026-11-11, `notes/SPLITS.md`):
  `adler32` 0x006A1860, `crc32` 0x006A1C10, `crc32_big` 0x006968A0, `deflate` 0x006A20E8,
  `deflateEnd` 0x006A3168, `deflateInit2_` 0x006A3248, `deflateReset` 0x006A34D4,
  `deflate_fast` 0x006974D4, `deflate_slow` 0x00698264, `deflate_stored` 0x00698B94,
  `fill_window` 0x0069912C, `flush_pending` 0x006994F0, `inflate` 0x006A360C,
  `inflateEnd` 0x006A4FB0, `inflateInit_` 0x006A4FFC (a tail call to `inflateInit2_`,
  which this copy does not inline), `inflateInit2_` 0x006A500C, `inflateReset`
  0x006A5150, `inflate_fast` 0x006A51E4, `updatewindow` 0x006B0CA8, `inflate_table`
  0x006A594C, `build_tree` 0x006951B4 (an LDR-only trailing pool in its size, like the
  SDK copy's), `compress_block` 0x00695E8C, `scan_tree` 0x006A6088, `send_tree`
  0x006A6718, `_tr_align` 0x006A0B2C, `_tr_flush_block` 0x006A0E2C, `_tr_init`
  0x006A153C, `_tr_stored_block` 0x006A168C, `zcalloc` 0x006A5F60, `zcfree` 0x006A5F68.
  It has no marker call. Two copies can not share a name in `symbols.txt` and the names
  this copy had in the image (a prefix?) are not known, so its functions keep their
  analysis names (`fn_<address>`); its units are compiled with
  `--preinclude=libs/zlib-1.2.5/stub/names.h`, which maps each zlib name to that
  `fn_<address>` (and its data, `lbl_<address>`). Those `#define`s are this project's
  file, not evidence of a name.

With 1.2.7 and `--cpu=MPCore`: `-O3 -Ospace` and `-O2 -Ospace` find none, `-O2 -Otime` one; `build_tree`
(1.2.5 copy) matches with builds 921, 1049, 1440, 1454 only, `inflate_fast` (1.2.5 copy)
with 894 and later; 4.0 and 4.1 b561 find none of them.

### BigRed sources (New Super Mario Bros. 2)

All 1811 objects of BigRed with their own flags: 285 functions found with 4.1
b844-b1454 (the same set), 283 with b791, 281 with b713, 109 with 4.1 b561 and every 4.0
build, 148 with 5.04. Mostly SDK and runtime code in 0x00100000-0x001BFFFF. Some names
there (sead) come from functions identical to generic code, and are not evidence that
this game uses those libraries.

### Flags of RedPepper (Super Mario 3D Land, 2026-11-11)

RedPepper builds its game, sead and nnsdk with `--apcs=//interwork --cpu=MPCore
--fpmode=fast --cpp --arm --force_new_nothrow --signed_chars --multibyte-chars
--locale=japanese --no_vfe --no_rtti_data --no_rtti --no_exceptions -O3 -Otime
--data-reorder --split_sections --forceinline` (another game, so a lead only). The flags
proven here are all in it. The three that are not in `cflags_base` were each added to it
and the project rebuilt (Squirrel, zlib 1.2.5, the game unit): `--data-reorder`,
`--force_new_nothrow`, `--multibyte-chars --locale=japanese` change nothing in the report
(no regression, no gain). Not proven, not ruled out; not added. `--locale=japanese` can
only matter for sources with Japanese literals, `--force_new_nothrow` for code with
`new`, `--data-reorder` for objects with several data items.

### First game unit

`SetFogDensity_` (0x002546FC, `src/game/FieldScriptFunc.cpp`) matches with b921 and the
base flags, and is linked from source. It is too small to tell builds apart (it also
matches with 4.0 and 5.04).

### Script bindings: ARM Compiler 5.04 (2026-11-11)

Each binding unit was built with each build (the game flags of `configure.py`) and its
functions counted at 100 % in the objdiff report.

`FieldScriptFunc.cpp` (186 functions): 181 with b921, 183 with 5.04 b82; `GetPos_` and
`SetAnalyzeInfo_` match with 5.04 only, none with b921 only.

`BattleScriptFunc.cpp` (140 functions):

| Build | Functions at 100 % |
|---|---|
| 4.0 b902 | 53 |
| 4.1 b921, b1049 | 105 |
| **5.04 b82** | **114** |

Every function that matches with b921 also matches with 5.04. Nine match with 5.04 only:
`SetHpMax_`, `SetMpMax_`, `SetHpDamage_`, `SetMpDamage_`, `SetHpMaxDamage_`,
`SetMpMaxDamage_`, `MonsterRevival_`, `SetEventFlg_`, `SetMonsterMeshVisible_`.

So `configure.py` sets `armcc_version="5.04/b82"` on the `game` library. Squirrel, built
with the game, matches with b921 (above) and finds 71 functions with 5.04: the image
holds code from at least two compilers. Which game files used which is open.

## Libraries seen in the image

| Library | Evidence |
|---|---|
| CTR-SDK | `nn::` error strings, e.g. `nn::ac::Initialize() failed` at 0x001ABA78 |
| zlib 1.2.7 (SDK build) | version string at 0x0047AFF4; functions above |
| zlib 1.2.5 | string `1.2.5` at 0x0073C75C; 30 functions above (second copy) |
| Squirrel 2.2.5 | version string at 0x001557C0; 224 functions above |
| NEX and PIA | `nn::nex::RootTransport` at 0x0074A596; `NN_PIA_SESSION_MAX_SILENCE_TIME_MAX` at 0x0073E509 |
| NintendoWare for CTR | `battle_font_0.bflim` at 0x007B3988, `break_font.bffnt` at 0x007BDBB0, `Eft_Ptcl_PlaneXY.vsh` at 0x007535A6 |
| Square Enix online library ("SIL") | `X-Sil-Version` at 0x0057918C, `dqmj3ds.sil2.square-enix.com` at 0x007BF80C |

No compiler identification string (`ARM C/C++ Compiler`, `RVCT`) is in `code.bin`.

## Open questions

- Whether every library (NintendoWare, NEX, PIA, SIL) was built with build 921 too.
  The CTR-SDK's zlib was not (b1049/1440/1454, `--cpu=MPCoreNoVFP`, above): prebuilt
  libraries need their own `armcc_version` and `--cpu`, so a sweep of a library should
  try every build with `--cpu=MPCore` and `--cpu=MPCoreNoVFP`.
- Thumb code (332 functions): which flags.
- The static initializer of `sqstate.cpp` (above): matches with 5.04 only.
- Which game files were built with 5.04 (the script bindings were, above) and which
  with 4.1 b921.

## Reproducing

```
python tools/compiler_sweep.py --project <BigRed clone>
python tools/compiler_sweep.py --flags "<flags> --no_dep_name" -I <sq>/include -I <sq>/squirrel <sq>/squirrel/*.cpp
python tools/compiler_sweep.py --flags "--c90 --arm --cpu=MPCore --apcs=/interwork --split_sections -O3 -Otime" -I <dir with an empty sys/types.h> -I <zlib> <zlib>/{adler32,crc32,deflate,inflate,inffast,inftrees,trees,zutil,compress,uncompr}.c
python tools/compiler_sweep.py --flags "--c90 --arm --cpu=MPCoreNoVFP --apcs=/interwork --split_sections -O3 -Otime" -I libs/zlib/stub -I libs/zlib libs/zlib/{adler32,crc32,deflate,inflate,inffast,inftrees,trees,zutil,compress,uncompr}.c
```

Under Git Bash, set `MSYS_NO_PATHCONV=1` so that `/interwork` is not turned into a path.
