# Compiler, SDK and runtime

What is known about how `code.bin` was built, with the evidence for each point.
Anything without evidence is marked as a hypothesis.

## Status

Not identified (roadmap step 2). `configure.py` uses RVCT 4.1 build 894 with the flags
BigRed found for New Super Mario Bros. 2:

```
--cpp --arm --cpu=MPCore --fpmode=fast --apcs=/interwork --split_sections -O3 -Otime
--no_rtti --no_rtti_data --signed_chars
```

These are **placeholders**: nothing in this game confirms them yet.

## Evidence so far

| Fact | Evidence |
|---|---|
| Built against the CTR-SDK | `nn::` error strings, e.g. `nn::ac::Initialize() failed` at 0x001ABA78 |
| zlib from the CTR-SDK | version string `1.2.7.f-NINTENDO-CTR-SDK-v1` at 0x0047AFF4 |
| NEX and PIA network libraries | `nn::nex::RootTransport` at 0x0074A596; `NN_PIA_SESSION_MAX_SILENCE_TIME_MAX` at 0x0073E509 |
| NintendoWare for CTR (layout, font, effects) | `battle_font_0.bflim` at 0x007B3988, `break_font.bffnt` at 0x007BDBB0, `Eft_Ptcl_PlaneXY.vsh` at 0x007535A6 |
| Square Enix online library ("SIL") | `X-Sil-Version` at 0x0057918C, `dqmj3ds.sil2.square-enix.com` at 0x007BF80C |
| Mostly ARM code, some Thumb | 332 of 34,058 functions are Thumb, in 0x00100000-0x0013FFFF and 0x002C0000-0x0033FFFF (`config/jpn/symbols.txt`); in BigRed, the Thumb functions are C library and SDK code |
| Short string literals sit in `.text` literal pools | `1.2.7.f-NINTENDO-CTR-SDK-v1` and `BattleScriptFunc.cpp` are in `.text`, which is what armcc does with literals shorter than 64 characters (`notes/BUILD_SYSTEM.md`) |

No compiler identification string (`ARM C/C++ Compiler`, `RVCT`) and no NintendoWare or
SDK version string has been found in `code.bin`.

## Candidates

decomp.me's `armcc.zip` holds RVCT 4.0 (b771, b821, b865, b902), RVCT 4.1 (b561, b713,
b791, b844, b894, b921, b1049, b1440, b1454) and ARM Compiler 5.04 (b82). For comparison:

- Ocarina of Time 3D (2011): RVCT 4.0 b821 (zeldaret/oot3d README).
- New Super Mario Bros. 2 (2012): RVCT 4.1, builds 713-1454 all match what BigRed has
  decompiled; 561 and 4.0 do not.

DQMJ3 was released in 2016, later than both: a later 4.1 build (1049, 1440, 1454) or
5.04 is plausible. **Hypothesis**, to be settled by step 2.

## Method (step 2)

1. Find small, self-contained functions whose source is known: RVCT C library and EABI
   helpers (`__aeabi_*`, `memcpy`, `strlen`), zlib 1.2.7 (public source), zeldaret/3ds_sdk
   `nn::` code.
2. Compile them with every build and flag set (`tools/compiler_sweep.py`, to port from
   DQMJ2), and search `code.bin` for byte-identical results (relocations masked).
3. Confirm with the first game unit at 100 % in objdiff; then record the build, the
   flags and the functions that decide them here.
