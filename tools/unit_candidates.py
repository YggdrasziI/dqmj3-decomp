#!/usr/bin/env python3
"""List small functions of code.bin that no source file claims yet.

Lists functions instead of units: for each function of symbols.txt that lies outside
every range claimed in splits.txt (that is, in an automatic `auto/` unit), its size,
the calls it makes and its callers. Calls are the R_ARM_CALL, R_ARM_JUMP24,
R_ARM_THM_CALL and R_ARM_THM_JUMP24 relocations of the split objects in
build/<version>/delink/ (direct calls and tail calls; calls through vtables or
function pointers are not counted). Call-tree leaves (no calls) come first, then by
size. A function whose callers are all close to it most likely shares their unit
(a hint, not a proof).

Run `ninja split` (or `ninja`) first so that the split objects match splits.txt.

Usage:
  python tools/unit_candidates.py              # 30 smallest leaves
  python tools/unit_candidates.py -n 50 --max-calls 2
  python tools/unit_candidates.py --start 0x00250000 --end 0x00260000
  python tools/unit_candidates.py --region <id>   # once config.toml has [[regions]]
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from ctr import elf  # noqa: E402
from ctr.image import VersionConfig  # noqa: E402
from ctr.symbols import Splits, SymbolTable  # noqa: E402

CALL_RELOCS = {elf.R_ARM_CALL, elf.R_ARM_JUMP24, elf.R_ARM_THM_CALL, elf.R_ARM_THM_JUMP24}
NEAR = 0x400


def read_calls(delink_dir, addr_of):
    """[(caller address, call site address, target name)] of every split object."""
    calls = []
    for path in sorted(delink_dir.rglob("*.o")):
        obj = elf.ElfFile.load(path)
        funcs = {}  # section index -> [(value, size, name)] of its defined functions
        for sym in obj.symbols:
            if sym.type == elf.STT_FUNC and sym.is_defined and sym.shndx < len(obj.sections):
                funcs.setdefault(sym.shndx, []).append((sym.value, sym.size, sym.name))
        for section in obj.sections:
            if not section.is_code:
                continue
            for reloc in section.relocs:
                if reloc.type not in CALL_RELOCS:
                    continue
                owner = next((f for f in funcs.get(section.index, ())
                              if f[0] <= reloc.offset < f[0] + max(f[1], 1)), None)
                if owner is None or owner[2] not in addr_of:
                    continue
                site = addr_of[owner[2]] + reloc.offset - owner[0]
                calls.append((addr_of[owner[2]], site, obj.symbols[reloc.symbol].name))
    return calls


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", default="jpn")
    parser.add_argument("-n", type=int, default=30, help="rows to print")
    parser.add_argument("--max-calls", type=int, default=0, help="most outgoing calls (default 0: leaves)")
    parser.add_argument("--min-size", type=lambda x: int(x, 0), default=8,
                        help="smallest size (default 8: skips 4-byte 'bx lr' stubs)")
    parser.add_argument("--start", type=lambda x: int(x, 0), help="lowest address")
    parser.add_argument("--end", type=lambda x: int(x, 0), help="end address (exclusive)")
    parser.add_argument("--region", help="id of a [[regions]] entry of config.toml")
    args = parser.parse_args()

    config = VersionConfig(ROOT / "config" / args.version / "config.toml")
    symbols = SymbolTable.load(ROOT / config.symbols_path)
    splits = Splits.load(ROOT / config.splits_path)
    delink_dir = ROOT / "build" / args.version / "delink"
    if not delink_dir.is_dir():
        sys.exit(f"{delink_dir.relative_to(ROOT)} is missing: run `ninja split` first")

    bounds = []
    if args.region:
        region = next((r for r in config.regions if r.id == args.region), None)
        if region is None:
            known = ", ".join(r.id for r in config.regions) or "none in config.toml"
            sys.exit(f"no region {args.region!r} (regions: {known})")
        bounds.append((region.start, region.end))
    if args.start is not None or args.end is not None:
        bounds.append((args.start or 0, args.end if args.end is not None else 1 << 32))

    funcs = sorted((s for s in symbols if s.is_function and s.section == ".text" and s.size),
                   key=lambda s: s.address)
    addr_of = {}
    for s in funcs:
        addr_of.setdefault(s.name, s.address)
    claimed = splits.claimed(".text")

    out_calls, callers = {}, {}
    for caller, site, target in read_calls(delink_dir, addr_of):
        out_calls[caller] = out_calls.get(caller, 0) + 1
        if target in addr_of:
            callers.setdefault(addr_of[target], []).append(site)

    rows = []
    for s in funcs:
        if s.size < args.min_size or any(a <= s.address < e for a, e in claimed):
            continue
        if not all(a <= s.address < e for a, e in bounds):
            continue
        n_calls = out_calls.get(s.address, 0)
        if n_calls > args.max_calls:
            continue
        who = callers.get(s.address, [])
        near = sum(1 for c in who if abs(c - s.address) < NEAR)
        rows.append((n_calls, s.size, s.address, s.name, "thumb" if s.thumb else "arm", len(who), near))
    rows.sort()
    print(f"{'address':<11} {'size':>6} {'mode':<5} {'calls':>5} {'callers':>7} {'near':>4}  name")
    for n_calls, size, addr, name, mode, n_callers, near in rows[:args.n]:
        print(f"0x{addr:08X} {size:>#6x} {mode:<5} {n_calls:>5} {n_callers:>7} {near:>4}  {name}")
    where = " in " + ", ".join(f"[0x{a:08X}, 0x{e:08X})" for a, e in bounds) if bounds else ""
    print(f"{len(rows)} functions (calls <= {args.max_calls}){where} not claimed by a unit; "
          f"'near' = call sites within 0x{NEAR:x} bytes")


if __name__ == "__main__":
    main()
