# Build system

Adapted from [BigRed](https://github.com/T3CHNOLOG1C/BigRed)'s `docs/build_system.md` (CC0), whose tools
this project uses (`notes/PROVENANCE.md`). Statements about New Super Mario Bros. 2 are marked as such.

The layout of this project follows [decomp-toolkit](https://github.com/encounter/decomp-toolkit) projects:
`configure.py` describes the project and generates `build.ninja` and `objdiff.json`, `config/<version>/` holds
`symbols.txt` and `splits.txt`, and [objdiff](https://github.com/encounter/objdiff) compares objects and
measures progress.

decomp-toolkit itself does not support the 3DS, and neither the original linker (`armlink`) nor the rest of
the RVCT toolchain is available, only the compiler. The tools in [`tools/ctr/`](../tools/ctr) fill that gap.
They are plain Python without dependencies.

- [Stages of a build](#stages-of-a-build)
- [The original image](#the-original-image)
- [Compiler](#compiler)
- [Splitting](#splitting)
- [Linking](#linking)
- [What the linker did to the code](#what-the-linker-did-to-the-code)
- [String literals](#string-literals)
- [Bootstrapping symbols.txt](#bootstrapping-symbolstxt)
- [Changes for this project](#changes-for-this-project)
- [Known gaps](#known-gaps)

## Stages of a build

| Stage   | Tool                   | Input                                | Output                         |
| ------- | ---------------------- | ------------------------------------ | ------------------------------ |
| compile | `armcc`                | `src/<unit>.cpp`                     | `build/jpn/src/<unit>.o`       |
| prelink | `tools/ctr/prelink.py` | `build/jpn/src/<unit>.o`             | `build/jpn/diff/<unit>.o`      |
| split   | `tools/ctr/split.py`   | `orig/jpn/code.bin`                  | `build/jpn/delink/<unit>.o`    |
| link    | `tools/ctr/link.py`    | objects of all `Matching` units      | `build/jpn/code.bin`           |
| check   | `tools/ctr/check.py`   | `build/jpn/code.bin`                 | `build/jpn/ok`                 |
| report  | `objdiff-cli`          | `build/jpn/delink/`, `build/jpn/diff/` | `build/jpn/report.json`      |
| image   | `tools/progress_image.py` | `build/jpn/report.json`           | `assets/progress.svg`          |

objdiff compares `build/jpn/delink/<unit>.o` (what the game contains) with `build/jpn/diff/<unit>.o` (what
the source compiles to).

The image stage (`tools/progress_image.py`) is disabled (`progress_image_title = None`); the README badges are
drawn by `tools/progress_badges.py` instead.

Useful targets: `ninja` builds everything and prints progress, `ninja check` stops after verifying the image,
`ninja split` only splits the original image.

`python configure.py --non-matching` links units marked `NonMatching` as well, defines `NON_MATCHING` for
the compiler, and skips the verification. The result is not expected to be identical to the original.

## The original image

`code.bin` is a flat dump of three segments that are mapped one after another starting at `0x00100000`. Their
addresses and sizes come from the extended header of the game and are recorded in
[`config/jpn/config.toml`](../config/jpn/config.toml) (table in `SPEC.md`).

### Libraries

Progress is measured per category: game, runtime and SDK, NintendoWare, network libraries, unidentified.
A unit listed in `configure.py` belongs to the library it is listed under. For everything else,
`config.toml` divides `.text` into `[[regions]]`, and the automatically generated units are named after the
region they are in. No region is defined yet: the region map is roadmap step 4 (`notes/SPLITS.md`).

In New Super Mario Bros. 2 the C++ part of the image is sorted by mangled name, so a library is not one block:
the non-const functions of a library are together, but its const functions are among the const functions of
everything else. Whether this game was laid out the same way is not checked yet.

## Compiler

RVCT 4.1 build 921 with the flags BigRed found for New Super Mario Bros. 2, confirmed for this game by
compiling Squirrel 2.2.5 and zlib 1.2.7 (`notes/COMPILER.md`).

## Splitting

`split.py` cuts the original image into one object per unit. Units are the source files listed in
`splits.txt`, plus automatically generated `auto/` units that cover whatever no source file claims yet in
64 KiB steps, so that progress is measured against the whole game.

The objects are shaped like the compiler's output:

- every function is in its own `i.<name>` section
- calls and tail calls become `R_ARM_CALL` and `R_ARM_JUMP24` relocations against the called function
- literal pool entries and words in data sections that hold the address of a symbol become `R_ARM_ABS32`
  relocations
- switch tables become relocations against a local `__switch$$` symbol, as the compiler emits them
- `$a`, `$t` and `$d` mark ARM code, Thumb code and data
- a vtable (a symbol named `_ZTV...`) is in a section of its own, `.constdata__ZTV...`
- a function symbol that has no size in `symbols.txt` becomes a second name for the function at its address

Which words of a function are instructions is determined by following its control flow
([`tools/ctr/arm.py`](../tools/ctr/arm.py)).

A word is taken to be an address if it has the value of an address inside the image at which a symbol exists.
An integer constant that happens to look like one becomes a relocation by mistake. That shows up as a
mismatch in objdiff on a line that otherwise looks identical.

## Linking

The split objects are only used for comparing. They are not linked.

`link.py` starts from the original image. For each `Matching` unit it clears the ranges the unit claims in
`splits.txt` and fills them from the compiled object. A section of the object goes to the address
`symbols.txt` gives the symbols defined in it, and every reference is resolved through `symbols.txt`. Ranges
that no unit claims keep the bytes of the original.

A section that defines no symbol at all goes to the lowest address in the unit's ranges that the sections
placed by symbol leave free, in the order the object lists them. Bytes of a range that nothing fills are set
to `0xFF`, which is what armlink padded the gaps between sections with.

This means that:

- The build can not shift anything. Code that is a different size than the original does not fit.
- A unit has to be complete. Every byte in the ranges it claims has to come out of its object.
- Every symbol a `Matching` unit defines or uses has to be in `symbols.txt` under the name the compiler gives
  it.

## What the linker did to the code

armlink changed the code in four ways. All of them have to be reproduced to get an identical image, and they
affect what the original looks like in objdiff.

**Unused functions were removed** (`armlink --remove`, and `--vfe` for virtual functions). A compiled object
routinely contains functions the game does not have: deleting destructors, inline functions that were inlined
everywhere, virtual functions nothing calls. `link.py` leaves out every section whose symbols are not in
`symbols.txt` and lists it as removed in `build/jpn/code.map`. A vtable entry that points to such a function
is 0 in the original, so `link.py` writes 0, and `prelink.py` does the same to the object objdiff sees. A
reference to a removed function from anywhere else is an error.

**`bl` to a Thumb function became `blx`.** Split objects contain `bl` again.

**Calls to trivial functions were inlined** (`armlink --inline`). A `bl` to a function that consists of
nothing but `bx lr` was replaced by `mov r0, r0`. A `bl` to a function that consists of one instruction and
`bx lr` was replaced by that instruction. (Observed in New Super Mario Bros. 2; to be confirmed for this game.)

Nothing records which function was called, so this is not undone when splitting. Instead `prelink.py` applies
the same replacement to the compiled object before objdiff sees it, and `link.py` applies it when linking.

**Tail calls were turned into fallthrough** (`armlink --tailreorder` and `--branchnop`). Where it could, the
linker placed a function that is tail called directly behind its caller and replaced the `b` between them
with `mov r0, r0`. Split objects contain the `b` again, and `link.py` replaces any unconditional branch to the
following instruction.

`mov r0, r0` (`0xE1A00000`) is therefore always the linker's doing. The `nop` (`0xE320F000`) that is all over
the game is not: the compiler emits it where it inlined an empty function itself.

## String literals

Where the compiler puts a string literal depends on how it is used, and each case is linked differently.

| The literal is                                 | The compiler puts it in                   | It is linked by                          |
| ---------------------------------------------- | ----------------------------------------- | ---------------------------------------- |
| used by code, shorter than 64 characters       | the literal pool of the function          | being part of the function               |
| used by code, 64 characters or longer          | a `.constdata` section without a symbol   | taking free space in the unit's ranges   |
| used by data, such as a table of names         | `.conststring` (`.constwstring` if wide)  | looking it up in the string pool         |

**Long literals** need the unit to claim the address range of the string in `.rodata`. There must be no
symbol at that address in `symbols.txt`: the compiled object has none either, and objdiff compares data
symbol by symbol.

**String pools.** `.conststring` and `.constwstring` are mergeable sections, and armlink merged them across
the whole program into one pool each. Their location is recorded in `config.toml` once found (not yet for
this game).

In a pool every string exists once, and a string that is the tail of another one does not exist on its own:
`"wait"` is the last four characters of `"bg_wait"`. If several strings end in the one being looked for, armlink
picked the one that comes last when comparing them character by character from the end. `tools/ctr/strpool.py`
follows the same rule, which reproduced every pointer into the two pools of New Super Mario Bros. 2.

A pool does not belong to any unit and can not be claimed in `splits.txt`. `link.py` gives a reference to a
pooled string the address that string has in the original, and fails if the original has no such string.
`split.py` does the reverse: for data that points into a pool it emits a `.conststring` section with just those
strings, so that it looks like the compiler's output.

## Bootstrapping symbols.txt

`symbols.txt` was generated once by `tools/ctr/analyze.py` and is maintained by hand from there on:

```sh
python tools/ctr/analyze.py config/jpn/config.toml
```

It finds functions by walking `.text` from the entry point. The extent of each function follows from its
control flow, and the next function starts where the previous one ends. Only call targets are trusted beyond
that. Words in data sections that look like code addresses are not, as too many of them are something else.

`--regenerate` discards all `fn_` and `lbl_` symbols and analyzes again while keeping every symbol that was
given a name. Use it after improving the analysis. Data inside ranges that a unit claims in `splits.txt` is
never labelled.

## Changes for this project

- `tools/ctr/analyze.py`: after ARM code, a function is only guessed to be Thumb if it starts with a Thumb
  `push`. Without that rule the data islands of `.text` (pointer tables, UTF-16 strings, around
  0x00640000-0x006C0000) were tiled as Thumb code: 65,632 functions, 26,127 of them Thumb. With it: 34,058
  functions, 332 Thumb.
- `tools/project.py`: the report command runs through `cmd /s /c` on Windows, where ninja starts commands
  without a shell.
- `tools/ctr/report_accounting.py`: the check of BigRed's total code size is removed.
- `tools/project.py`: on Windows the compiler is started with a native path (`CreateProcess` does not
  search a relative path written with `/`).
- `tools/ctr/linker.py`: a data section whose only symbols are locals that `symbols.txt` does not know is
  placed in the unit's free space, like a section without symbols. armcc puts each function's `__FUNCTION__`
  string in a `.constdata` section with a local symbol named `__FUNCTION__`; such a string needs its `.rodata`
  range claimed in `splits.txt` and no symbol at its address in `symbols.txt`.
- `tools/ctr/prelink.py`: `R_ARM_NONE` relocations are dropped from the object objdiff reads. armcc emits them
  against `_printf_*` so that armlink pulls in the format handlers a format string needs; they change no
  bytes, the linker ignores them, and objdiff can not read them.
- `tools/ctr/prelink.py`: armcc puts template instances in `t.<name>` sections, other functions in
  `i.<name>`. Split objects only have `i.`, and objdiff pairs functions by section name, so `t.` is renamed
  to `i.` in the object objdiff reads.

## Known gaps

- **Function boundaries are a starting point.** 32 functions have control flow the analysis could not follow,
  and the boundaries inside the C library at the start of `.text` are unreliable. A function that is only
  reached by a tail call that the linker did not reorder is still part of the function in front of it. Fix
  `symbols.txt` when you run into one.
- **Sections without a symbol are placed in order.** That is right for the one `.constdata` section that
  long string literals end up in. A unit whose object has several such sections of the same kind relies on
  the free space in its ranges being in the same order.
- **Strings the code points into pools with.** No code in the game refers to a pooled string directly, only
  data does, so `split.py` does not look for that.
- **Sections shared between units** (inline functions, vtables) are only linked by a unit that claims their
  address.
- **Data symbols are coarse.** A data symbol starts where something points to and ends at the next one. Most
  cover several objects.
- **No exception tables.** `.ARM.exidx` and `.ARM.extab` sections of compiled objects are ignored.
- **One version.** Only the Japanese release is set up.
