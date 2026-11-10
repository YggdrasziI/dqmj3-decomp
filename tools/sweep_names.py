#!/usr/bin/env python3
"""
Names functions in symbols.txt from a compiler sweep.

A reference function compiled with the game's compiler and found byte for byte
(relocations masked) at exactly one address of the image is evidence that the
function at that address is the reference function. This applies the reference's
(mangled) names to symbols.txt.

A name is applied only when:
  - the sweep found the function at exactly one address with the given build;
  - symbols.txt has a function starting at that address whose name is still an
    analysis name (fn_<address>);
  - no other function of the sweep was found at the same address;
  - the name is not already used by another symbol;
  - our sources (src/, include/, libs/) do not use the analysis name.
Functions whose size in symbols.txt differs from the compiled size are reported (the
analysis bounds may be wrong); the size is corrected only with --fix-sizes.

Usage:
    python tools/sweep_names.py build/sweep_sq.json --build 4.1/b921 [--dry-run] [--fix-sizes]
"""

import argparse
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYMBOLS = ROOT / "config" / "jpn" / "symbols.txt"
LINE = re.compile(r"^(?P<name>\S+) = (?P<section>\.\w+):0x(?P<addr>[0-9A-Fa-f]+);(?P<rest>.*)$")
AUTO = re.compile(r"^fn_[0-9A-F]{8}$")


def names_in_sources():
    """Analysis names (fn_/lbl_) that our sources use: renaming them would break the build."""
    found = set()
    for top in ("src", "include", "libs"):
        for path in (ROOT / top).rglob("*"):
            if path.suffix in (".c", ".cpp", ".h", ".hpp", ".inc", ".s"):
                found.update(re.findall(r"\b(?:fn|lbl)_[0-9A-F]{8}\b", path.read_text(encoding="utf-8", errors="replace")))
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("sweep", type=Path, help="JSON written by compiler_sweep.py --json")
    parser.add_argument("--build", default="4.1/b921")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--fix-sizes", action="store_true")
    args = parser.parse_args()

    results = json.loads(args.sweep.read_text())
    found = {}
    for name, entry in results.items():
        hit = entry.get(args.build)
        if isinstance(hit, str) and hit.startswith("0x"):
            found[name] = (int(hit, 16), entry.get("sizes", {}).get(args.build, entry["size"]))
    per_addr = collections.Counter(addr for addr, _ in found.values())

    lines = SYMBOLS.read_text(encoding="utf-8").splitlines()
    by_addr = {}
    used = set()
    for i, line in enumerate(lines):
        m = LINE.match(line)
        if not m:
            continue
        used.add(m["name"])
        if "type:function" in m["rest"]:
            by_addr[int(m["addr"], 16)] = i

    in_sources = names_in_sources()
    renamed, skipped = 0, collections.Counter()
    size_notes = []
    for name, (addr, size) in sorted(found.items(), key=lambda kv: kv[1][0]):
        if per_addr[addr] > 1:
            skipped["several sweep functions at one address"] += 1
            continue
        i = by_addr.get(addr)
        if i is None:
            skipped["no function starts there in symbols.txt"] += 1
            print(f"  no function at 0x{addr:08X} for {name}")
            continue
        m = LINE.match(lines[i])
        if m["name"] in in_sources:
            skipped["analysis name used by our sources"] += 1
            print(f"  {m['name']} is used in src/, include/ or libs/: not renamed to {name}")
            continue
        if not AUTO.match(m["name"]):
            skipped["already named" if m["name"] != name else "already this name"] += 1
            continue
        if name in used:
            skipped["name already used elsewhere"] += 1
            print(f"  {name} already in symbols.txt, not applied at 0x{addr:08X}")
            continue
        rest = m["rest"]
        sm = re.search(r"size:0x([0-9A-Fa-f]+)", rest)
        if sm and int(sm.group(1), 16) != size:
            size_notes.append(f"  0x{addr:08X} {name}: symbols.txt size 0x{int(sm.group(1), 16):X}, compiled 0x{size:X}")
            if args.fix_sizes:
                rest = rest.replace(sm.group(0), f"size:0x{size:X}")
        lines[i] = f"{name} = {m['section']}:0x{m['addr']};{rest}"
        used.add(name)
        renamed += 1

    print(f"{renamed} functions named from {args.sweep.name} ({args.build})")
    for reason, count in skipped.items():
        print(f"  skipped, {reason}: {count}")
    if size_notes:
        print(f"{len(size_notes)} size differences{' (fixed)' if args.fix_sizes else ''}:")
        print("\n".join(size_notes))
    if not args.dry_run:
        SYMBOLS.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
