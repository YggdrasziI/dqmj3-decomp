#!/usr/bin/env python3
"""Show one function of a unit next to the original, from objdiff's own diff.

Runs `objdiff-cli diff` (same matching as the objdiff GUI and report) and prints
the original (left) and our build (right) side by side:

  ' ' same   '|' argument differs   'o' opcode differs   'r' replaced
  '<' only in the original           '>' only in our build

Usage:
  python tools/asm_compare.py game/FieldScriptFunc _Z14SetFogDensity_P4SQVM
  python tools/asm_compare.py sqapi sq_getfloat
  python tools/asm_compare.py --objects <original.o> <ours.o> _Z14SetFogDensity_P4SQVM

Unit names are objdiff's (`objdiff.json`: `game/FieldScriptFunc`, `squirrel/sqapi`,
`auto/text_00190000`); a unique last component (`sqapi`) is enough. Needs
`objdiff.json` (`python configure.py`) and a built unit (`ninja`). With --objects any
two ELF objects are compared, e.g. a scratch variant against the split original in
build/jpn/delink/.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBJDIFF = os.path.join(ROOT, "build", "tools", "objdiff-cli.exe" if os.name == "nt" else "objdiff-cli")

MARKS = {
    None: " ",
    "DIFF_ARG_MISMATCH": "|",
    "DIFF_OP_MISMATCH": "o",
    "DIFF_REPLACE": "r",
    "DIFF_DELETE": "<",
    "DIFF_INSERT": ">",
}


def load_units():
    with open(os.path.join(ROOT, "objdiff.json"), encoding="utf-8") as f:
        return json.load(f)["units"]


def unit_name(short):
    """Full objdiff unit name from a short one (sqapi -> squirrel/sqapi)."""
    names = [u["name"] for u in load_units()]
    if short in names:
        return short
    matches = [n for n in names if n.endswith("/" + short)]
    if len(matches) != 1:
        sys.exit(f"unit {short!r}: {len(matches)} matches in objdiff.json")
    return matches[0]


def run_diff(cmd_head, symbol):
    """objdiff-cli's JSON diff of one symbol; cmd_head selects the unit or the objects."""
    with tempfile.TemporaryDirectory() as tmp:
        out_json = os.path.join(tmp, "diff.json")
        cmd = cmd_head + [symbol, "-o", out_json, "--format", "json"]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        if res.returncode != 0 or not os.path.exists(out_json):
            sys.exit(res.stderr.strip() or "objdiff-cli diff failed")
        with open(out_json, encoding="utf-8") as f:
            return json.load(f)


def unit_cmd(unit):
    return [OBJDIFF, "diff", "-p", ROOT, "-u", unit_name(unit)]


def objects_cmd(original, ours):
    # objdiff-cli runs in ROOT: paths are taken from the caller's directory
    return [OBJDIFF, "diff", "-1", os.path.abspath(original), "-2", os.path.abspath(ours)]


def rows(symbol_json):
    out = []
    for ins in symbol_json.get("instructions", []):
        text = ins.get("instruction", {}).get("formatted", "")
        out.append((ins.get("diff_kind"), text))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("args", nargs="+", help="<unit> <symbol>, or <symbol> with --objects")
    parser.add_argument("--objects", nargs=2, metavar=("ORIGINAL", "OURS"))
    opts = parser.parse_args()

    if opts.objects:
        if len(opts.args) != 1:
            sys.exit("with --objects give only the symbol")
        symbol = opts.args[0]
        diff = run_diff(objects_cmd(*opts.objects), symbol)
    else:
        if len(opts.args) != 2:
            sys.exit(__doc__)
        symbol = opts.args[1]
        diff = run_diff(unit_cmd(opts.args[0]), symbol)

    sides = []
    for side in ("left", "right"):
        # An automatic unit (auto/...) has no source, so no right side.
        found = [s for s in diff.get(side, {}).get("symbols", []) if s.get("name") == symbol]
        sides.append(found[0] if found else {})
    if not sides[0] and not sides[1]:
        sys.exit(f"{symbol} not found")
    left, right = rows(sides[0]), rows(sides[1])
    pct = sides[1].get("match_percent", sides[0].get("match_percent"))
    print(f"{symbol}: {pct:.2f} %" if pct is not None else f"{symbol}: no match data")
    print(f"  {'original':<44} | ours")
    for i in range(max(len(left), len(right))):
        kind, a = left[i] if i < len(left) else (None, "")
        kind_b, b = right[i] if i < len(right) else (None, "")
        mark = MARKS.get(kind or kind_b, "?")
        print(f"{mark} {a[:44]:<44} | {b}")


if __name__ == "__main__":
    main()
