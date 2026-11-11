# Compiler, SDK and runtime

What is known about how `code.bin` was built, with the evidence for each point.
Anything without evidence is marked as a hypothesis.

## Summary

| Item | Value | Status |
|---|---|---|
| Compiler (game code) | RVCT 4.1 build 921 (`armcc`) | proven among the 14 builds of decomp.me's `armcc.zip` (Squirrel sweep) |
| Compiler (CTR-SDK zlib) | RVCT 4.1, build 921 or later | proven (zlib sweep); exact build open |
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
  0x0069F0D8, 0x0069F240). Its `inflateInit2_` (0x0069F0DC) and deflate init
  (0x0069D2AC) point to an 8-byte default allocator, `mul r0, r1, r2; b fn_002FE59C`
  (0x006A0010): `zcalloc` of 1.2.7 built **without** `Z_SOLO` (with `Z_SOLO` there is no
  default allocator). Source: zlib 1.2.7, no `Z_SOLO`, `zconf.h` without
  `<sys/types.h>` (armcc 4.1 has none), `--c90` and the C flags of `configure.py`.
  Found with build 921: `_tr_align`, `_tr_flush_bits`, `_tr_init`, `_tr_stored_block`,
  `inflateInit_`, `inflateReset`, `deflateBound`; `inflateInit2_` is named from the tail
  call of `inflateInit_` but differs from the public source (0x164 bytes, 0x144 in 1.2.7).
- **zlib 1.2.5**: called from the network block (0x0040F940, which refers to the string
  `1.2.5` at 0x0073C75C, calls `deflateInit2_` 0x006A3248). zlib 1.2.5 (public release)
  with the same flags (an empty `sys/types.h` on the include path) finds 20 functions with
  build 921 (22 with 1049, 1440, 1454; 19 with 894), all in this component:
  `deflate_fast` 0x006974D4, `deflate_slow` 0x00698264, `deflate_stored` 0x00698B94,
  `fill_window` 0x0069912C, `flush_pending` 0x006994F0, `deflateInit2_` 0x006A3248,
  `deflateReset` 0x006A34D4, `inflateInit2_` 0x006A500C, `inflateReset` 0x006A5150,
  `inflate_fast` 0x006A51E4, `updatewindow` 0x006B0CA8, `build_tree` 0x006951B4,
  `compress_block` 0x00695E8C, `send_tree` 0x006A6718, `_tr_align` 0x006A0B2C,
  `_tr_flush_block` 0x006A0E2C, `_tr_init` 0x006A153C, `_tr_stored_block` 0x006A168C. Its
  default allocator is 0x006A5F60. Not named: two copies can not share a name in
  `symbols.txt`, and the names of this copy (a prefix?) are not known.

With 1.2.7: `-O3 -Ospace` and `-O2 -Ospace` find none, `-O2 -Otime` one; `build_tree`
(1.2.5 copy) matches with builds 921, 1049, 1440, 1454 only, `inflate_fast` (1.2.5 copy)
with 894 and later; 4.0 and 4.1 b561 find none of them.

### BigRed sources (New Super Mario Bros. 2)

All 1811 objects of BigRed with their own flags: 285 functions found with 4.1
b844-b1454 (the same set), 283 with b791, 281 with b713, 109 with 4.1 b561 and every 4.0
build, 148 with 5.04. Mostly SDK and runtime code in 0x00100000-0x001BFFFF. Some names
there (sead) come from functions identical to generic code, and are not evidence that
this game uses those libraries.

### First game unit

`SetFogDensity_` (0x002546FC, `src/game/FieldScriptFunc.cpp`) matches with b921 and the
base flags, and is linked from source. It is too small to tell builds apart (it also
matches with 4.0 and 5.04).

## Libraries seen in the image

| Library | Evidence |
|---|---|
| CTR-SDK | `nn::` error strings, e.g. `nn::ac::Initialize() failed` at 0x001ABA78 |
| zlib 1.2.7 (SDK build) | version string at 0x0047AFF4; functions above |
| zlib 1.2.5 | string `1.2.5` at 0x0073C75C; functions above (second copy) |
| Squirrel 2.2.5 | version string at 0x001557C0; 224 functions above |
| NEX and PIA | `nn::nex::RootTransport` at 0x0074A596; `NN_PIA_SESSION_MAX_SILENCE_TIME_MAX` at 0x0073E509 |
| NintendoWare for CTR | `battle_font_0.bflim` at 0x007B3988, `break_font.bffnt` at 0x007BDBB0, `Eft_Ptcl_PlaneXY.vsh` at 0x007535A6 |
| Square Enix online library ("SIL") | `X-Sil-Version` at 0x0057918C, `dqmj3ds.sil2.square-enix.com` at 0x007BF80C |

No compiler identification string (`ARM C/C++ Compiler`, `RVCT`) is in `code.bin`.

## Open questions

- Whether every library (NintendoWare, NEX, PIA, SIL) was built with build 921 too.
  Prebuilt libraries may need their own `armcc_version` per object.
- Thumb code (332 functions): which flags.
- The static initializer of `sqstate.cpp` (above): matches with 5.04 only.

## Reproducing

```
python tools/compiler_sweep.py --project <BigRed clone>
python tools/compiler_sweep.py --flags "<flags> --no_dep_name" -I <sq>/include -I <sq>/squirrel <sq>/squirrel/*.cpp
python tools/compiler_sweep.py --flags "--c90 --arm --cpu=MPCore --apcs=/interwork --split_sections -O3 -Otime" -I <dir with an empty sys/types.h> -I <zlib> <zlib>/{adler32,crc32,deflate,inflate,inffast,inftrees,trees,zutil,compress,uncompr}.c
```

Under Git Bash, set `MSYS_NO_PATHCONV=1` so that `/interwork` is not turned into a path.
