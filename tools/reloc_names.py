#!/usr/bin/env python3
"""
Names the targets of calls and references of matched functions in symbols.txt.

A function whose bytes match the original (objdiff 100 % with relocation targets
ignored, the report's default) makes the same calls and references, at the same
offsets, as the original. Where the original refers to an analysis name
(fn_<addr> / lbl_<addr>) and our compiled object refers to a real name at the same
offset, with the same relocation type and the same addend, the analysis name is that
real name.

A name is applied only when:
  - every matched function that refers to the analysis name agrees on the real name,
    and no other analysis name is given the same real name;
  - the real name is a global or weak symbol of our object (not a section, a local
    or a mapping symbol) and is not already in symbols.txt;
  - our sources (src/, include/, libs/) do not use the analysis name;
  - a call (R_ARM_CALL / JUMP24 / PC24) targets a function of symbols.txt.

Run `ninja` first: it reads build/jpn/report.json and the objects in
build/jpn/delink/ and build/jpn/diff/.

Usage:
    python tools/reloc_names.py [--dry-run]
"""

import argparse
import collections
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from ctr import elf  # noqa: E402

SYMBOLS = ROOT / "config" / "jpn" / "symbols.txt"
REPORT = ROOT / "build" / "jpn" / "report.json"
DELINK = ROOT / "build" / "jpn" / "delink"
DIFF = ROOT / "build" / "jpn" / "diff"
LINE = re.compile(r"^(?P<name>\S+) = (?P<section>\.\w+):0x(?P<addr>[0-9A-Fa-f]+);(?P<rest>.*)$")
AUTO = re.compile(r"^(fn|lbl)_[0-9A-F]{8}$")
CALLS = (elf.R_ARM_CALL, elf.R_ARM_JUMP24, elf.R_ARM_PC24)


def names_in_sources():
    """Analysis names (fn_/lbl_) that our sources use: renaming them would break the build."""
    found = set()
    for top in ("src", "include", "libs"):
        for path in (ROOT / top).rglob("*"):
            if path.suffix in (".c", ".cpp", ".h", ".hpp", ".inc", ".s"):
                found.update(re.findall(r"\b(?:fn|lbl)_[0-9A-F]{8}\b", path.read_text(encoding="utf-8", errors="replace")))
    return found


def function_relocs(obj, name):
    """{offset: (type, target name, bind, addend word)} of the section of function `name`."""
    for sym in obj.symbols:
        if sym.name == name and sym.is_defined and sym.shndx < len(obj.sections):
            section = obj.sections[sym.shndx]
            if not section.is_code:
                continue
            out = {}
            for r in section.relocs:
                target = obj.symbols[r.symbol]
                word = struct.unpack_from("<I", section.data, r.offset)[0] if r.offset + 4 <= len(section.data) else 0
                addend = word & 0x00FFFFFF if r.type in CALLS else word
                out[r.offset] = (r.type, target.name, target.bind, target.type, addend)
            return out
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    report = json.loads(REPORT.read_text(encoding="utf-8"))
    lines = SYMBOLS.read_text(encoding="utf-8").splitlines()
    index, used, functions = {}, set(), set()
    for i, line in enumerate(lines):
        m = LINE.match(line)
        if m:
            index[m["name"]] = i
            used.add(m["name"])
            if "type:function" in m["rest"]:
                functions.add(m["name"])

    proposals = collections.defaultdict(set)  # analysis name -> real names
    sources = collections.defaultdict(list)
    objects = {}
    for unit in report["units"]:
        name = unit["name"]
        if name.startswith("auto/"):
            continue
        matched = [f["name"] for f in unit.get("functions", []) if f.get("fuzzy_match_percent") == 100]
        if not matched:
            continue
        paths = (DELINK / f"{name}.o", DIFF / f"{name}.o")
        if not all(p.is_file() for p in paths):
            continue
        orig, ours = objects.setdefault(name, tuple(elf.ElfFile.load(p) for p in paths))
        for fn in matched:
            a, b = function_relocs(orig, fn), function_relocs(ours, fn)
            if a is None or b is None:
                continue
            for offset, (rtype, target, _, _, addend) in a.items():
                if not AUTO.match(target) or offset not in b:
                    continue
                otype, real, bind, stype, oaddend = b[offset]
                if real == target:  # our source uses the analysis name too
                    continue
                if otype != rtype or oaddend != addend:
                    continue
                if bind not in (elf.STB_GLOBAL, elf.STB_WEAK) or real.startswith(("$", "__tagsym$$")):
                    continue
                proposals[target].add(real)
                sources[target].append(f"{name}:{fn}+0x{offset:X}")

    owners = collections.defaultdict(set)
    for target, reals in proposals.items():
        for real in reals:
            owners[real].add(target)

    in_sources = names_in_sources()
    renamed, skipped = [], collections.Counter()
    for target in sorted(proposals):
        reals = proposals[target]
        if len(reals) != 1:
            skipped["references disagree"] += 1
            print(f"  {target}: several names {sorted(reals)}")
            continue
        real = next(iter(reals))
        if len(owners[real]) != 1:
            skipped["one name for several targets"] += 1
            print(f"  {real}: several targets {sorted(owners[real])}")
            continue
        if real in used:
            skipped["name already in symbols.txt"] += 1
            print(f"  {real} already in symbols.txt, not given to {target}")
            continue
        if target in in_sources:
            skipped["analysis name used by our sources"] += 1
            print(f"  {target} is used in src/, include/ or libs/: not renamed to {real}")
            continue
        if target not in index:
            skipped["target not in symbols.txt"] += 1
            continue
        if target.startswith("fn_") != (target in functions):
            skipped["not a function"] += 1
            continue
        i = index[target]
        m = LINE.match(lines[i])
        lines[i] = f"{real} = {m['section']}:0x{m['addr']};{m['rest']}"
        used.add(real)
        renamed.append((target, real, sources[target][0]))

    for target, real, where in renamed:
        print(f"{target} -> {real}  (from {where})")
    print(f"{len(renamed)} symbols named")
    for reason, count in skipped.items():
        print(f"  skipped, {reason}: {count}")
    if not args.dry_run:
        SYMBOLS.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
