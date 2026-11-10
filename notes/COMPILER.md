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
A function counts when it is found at exactly one address.

### Squirrel 2.2.5 (compiled with the game)

`"Squirrel 2.2.5 stable"` at 0x00155C40. Source: the 2.2.5 stable release
(`squirrel_2.2.5_stable.tar.gz`, zlib license), the 11 files of `squirrel/`, flags of
`configure.py` plus `--no_dep_name`. 385 functions compiled.

| Build | Functions found |
|---|---|
| 4.0 b771, b821, b865 | 35 |
| 4.0 b902, 4.1 b561 | 36 |
| 4.1 b713 | 218 |
| 4.1 b791 | 235 |
| 4.1 b844 | 239 |
| 4.1 b894 | 234 |
| **4.1 b921** | **244** |
| 4.1 b1049, b1440, b1454 | 240 (the same 240) |
| 5.04 b82 | 76 |

Build 921 finds every function the other 4.1 builds find. Outside 4.1, three functions
are found that b921 does not find at a single address: `weakref_ref` and
`closure_bindenv` (28 bytes each, both at 0x001B098C with 4.0: identical small code,
ambiguous with b921), and `__sti___11_sqstate_cpp__null_` (the static initializer of
`sqstate.cpp`, 192 bytes at 0x00655B48, 5.04 only; open question). What rules the
other builds out:

- found with b921 but not b1049 / b1440 / b1454: `SQFunctionProto::Load` (0x002694FC,
  9344 bytes), `SQCompiler::CreateFunction` (0x0019B970, 1104 bytes),
  `SQCompiler::CompExp` (0x0019D620), `SQCompiler::BitwiseAndExp` (0x001C174C);
- found with b921 but not b894 (10), among them `SQVM::ARITH_OP` (0x0019774C, 944
  bytes, b921 and later only), `SQCompiler::PrefixedExpr` (0x00199330, 1984 bytes),
  `SQLexer::ReadString` (0x00190DAC, 2248 bytes).

Flags, with b921 (functions found): base flags 244; `-O3 -Ospace` 36; `-O2 -Otime` 53;
without `--fpmode=fast` 243; without `--signed_chars` 235; without `--no_rtti` 244.

The 244 functions cover 96,284 bytes; 15 more are found at several addresses. The rest
differ (game changes to Squirrel, inlining across files, or code the linker removed) and
are not analysed yet.

### zlib 1.2.7 (CTR-SDK build)

Version string `1.2.7.f-NINTENDO-CTR-SDK-v1` at 0x0047AFF4. Source: zlib 1.2.7 (public
release), `-DZ_SOLO`, `--c90` and the C flags of `configure.py`. 60 functions compiled
with `-O3 -Otime`; `-O3 -Ospace` and `-O2 -Ospace` find none, `-O2 -Otime` one.

- `build_tree` (0x006951B4, 1928 bytes): builds 921, 1049, 1440, 1454 only.
- `inflate_fast` (0x006A51E4, 2192 bytes): 894 and later.
- 4.0 and 4.1 b561: none of the 11.

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
| Squirrel 2.2.5 | version string at 0x00155C40; 244 functions above |
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
python tools/compiler_sweep.py --flags "--c90 --arm --cpu=MPCore --apcs=/interwork --split_sections -DZ_SOLO -O3 -Otime" -I <zlib> <zlib>/{adler32,crc32,deflate,inflate,inffast,inftrees,trees,zutil,compress,uncompr}.c
```

Under Git Bash, set `MSYS_NO_PATHCONV=1` so that `/interwork` is not turned into a path.
