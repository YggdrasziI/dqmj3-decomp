#!/usr/bin/env python3
"""Explain why a near-matching function differs from the original.

Reads objdiff's row alignment of one function and sorts every differing row
into a kind, so that the source change to try follows from the kind:

  register  same instruction, other registers (core or VFP). The rows are summed
            up as a register permutation (ours -> original) with the source lines
            that use each register; a cycle among the callee-saved r4-r11 points
            to the order registers were allocated in.
  stack     same instruction, other sp offset: stack slot order of locals or
            temporaries.
  moved     an instruction present on both sides at another place (a delete
            and an insert with the same text once registers are masked): a
            scheduling choice.
  extra     an instruction only in our code; missing: only in the original.
            These are real code differences.
  other     anything else (constants, symbols, opcodes).

Literal pool offsets and branch targets that differ only because code moved
are not counted. Source lines are objdiff's line numbers, only present when the
object has line information (armcc -g); otherwise they are blank.

The kinds and what they suggest come from DQMJ2's mwccarm work (its
notes/MATCHING.md, "Diagnosing a gap"); how far they carry over to armcc is
not established yet.

Usage:
  python tools/why_diff.py <unit> <symbol> [--rows]
  python tools/why_diff.py --objects <original.o> <ours.o> <symbol> [--rows]

Unit names as in tools/asm_compare.py (objdiff's, e.g. game/FieldScriptFunc).
With --objects any two ELF objects are compared, e.g. a scratch variant against
the split original in build/jpn/delink/.
"""

import argparse
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import asm_compare  # noqa: E402

REG = re.compile(r"\b(r\d+|sp|lr|pc|ip|s\d+|d\d+)\b")
CALLEE = {f"r{n}" for n in range(4, 12)}


def load_rows(unit, symbol, objects=None):
    """Aligned rows of one function; `objects` = (original, ours) instead of a unit."""
    if objects:
        diff = asm_compare.run_diff(asm_compare.objects_cmd(*objects), symbol)
    else:
        diff = asm_compare.run_diff(asm_compare.unit_cmd(unit), symbol)
    sides = []
    for side in ("left", "right"):
        found = [s for s in diff.get(side, {}).get("symbols", []) if s.get("name") == symbol]
        if not found:
            sys.exit(f"{symbol} not found on the {side} side")
        sides.append(found[0])
    rows = []
    for a, b in zip(sides[0].get("instructions", []), sides[1].get("instructions", [])):
        ia, ib = a.get("instruction", {}), b.get("instruction", {})
        rows.append({
            "kind": a.get("diff_kind") or b.get("diff_kind"),
            "orig": ia.get("formatted", ""), "ours": ib.get("formatted", ""),
            "line": ib.get("line_number"),
            "orig_args": [p["arg"] for p in ia.get("parts", []) if "arg" in p],
            "ours_args": [p["arg"] for p in ib.get("parts", []) if "arg" in p],
        })
    last = None  # rows only in the original take the line of the row before
    for row in rows:
        if row["line"] is None:
            row["line"] = last
        last = row["line"]
    return rows, sides[1].get("match_percent")


def masked(text):
    text = REG.sub("R", text)
    return re.sub(r"\(->0x[0-9a-f]+\)", "", text).strip()


def arg_text(arg):
    if not arg:
        return ""
    return str(next(iter(arg.values())))


def classify(row):
    """Kind of a row whose two sides hold an instruction."""
    a, b = row["orig"], row["ours"]
    if a.split(" ")[0] != b.split(" ")[0]:
        return "other"
    # A load from the literal pool, or (armcc) the address of a literal in it:
    # only the pc offset differs when code moved
    pool = re.compile(r"(?:ldr|add) (r\d+), (?:\[pc, #0x[0-9a-f]+\]|pc, #0x[0-9a-f]+$)")
    if pool.match(a) and pool.match(b):
        return "pool" if pool.match(a).group(1) == pool.match(b).group(1) else "register"
    # Only branches inside the function: a call to another target is a real difference
    # (bl, blx, bl<cond>, blx<cond>; b<cond> such as ble or bls has three letters)
    op = a.split(" ")[0]
    if op in ("bl", "blx") or (op.startswith("blx") and len(op) == 5) or (op.startswith("bl") and len(op) == 4):
        return "other"
    if a.split(" ")[0].startswith("b") and REG.sub("R", a).split(" ")[0] == b.split(" ")[0] \
            and re.fullmatch(r"b\w* 0x[0-9a-f]+", a) and re.fullmatch(r"b\w* 0x[0-9a-f]+", b):
        return "branch"
    ra, rb = REG.findall(a), REG.findall(b)
    if masked(a) == masked(b) and ra != rb:
        return "register"
    if REG.sub("R", a) == REG.sub("R", b):
        return "register"
    if "sp" in a and "sp" in b:
        na = re.sub(r"#-?0x[0-9a-f]+|#-?\d+", "#", REG.sub("R", a))
        nb = re.sub(r"#-?0x[0-9a-f]+|#-?\d+", "#", REG.sub("R", b))
        if na == nb:
            return "stack"
    return "other"


def analyse(rows, window=16):
    kinds = []
    for i, row in enumerate(rows):
        k = row["kind"]
        if k is None:
            kinds.append(None)
        elif k == "DIFF_DELETE":
            kinds.append("missing")
        elif k == "DIFF_INSERT":
            kinds.append("extra")
        else:
            kinds.append(classify(row))
    # Pair a delete with an insert of the same masked text nearby: a move.
    moves = []
    used = set()
    for i, k in enumerate(kinds):
        if k != "missing":
            continue
        text = masked(rows[i]["orig"])
        best = None
        for j in range(max(0, i - window), min(len(rows), i + window + 1)):
            if j in used or kinds[j] != "extra":
                continue
            if masked(rows[j]["ours"]) == text and (best is None or abs(j - i) < abs(best - i)):
                best = j
        if best is not None:
            used.add(best)
            kinds[i] = kinds[best] = "moved"
            moves.append((i, best))
    return kinds, moves


def permutation(rows, kinds):
    """Register pairs (ours, original) over the instructions present on both sides."""
    pairs = Counter()
    lines = defaultdict(set)
    for row, k in zip(rows, kinds):
        if k not in (None, "register", "stack", "pool"):
            continue
        ra, rb = REG.findall(row["orig"]), REG.findall(row["ours"])
        if len(ra) != len(rb):
            continue
        for x, y in zip(rb, ra):
            pairs[(x, y)] += 1
            if x != y and row["line"]:
                lines[(x, y)].add(row["line"])
    return pairs, lines


def cycles(mapping):
    seen, out = set(), []
    for start in mapping:
        if start in seen:
            continue
        cyc, r = [], start
        while r in mapping and r not in seen:
            seen.add(r)
            cyc.append(r)
            r = mapping[r]
        if len(cyc) > 1 and r == start:
            out.append(cyc)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("args", nargs="+", help="<unit> <symbol>, or <symbol> with --objects")
    ap.add_argument("--objects", nargs=2, metavar=("ORIGINAL", "OURS"))
    ap.add_argument("--rows", action="store_true", help="print every differing row with its kind")
    opts = ap.parse_args()
    if len(opts.args) != (1 if opts.objects else 2):
        ap.error("give <unit> <symbol>, or <symbol> with --objects")
    opts.symbol = opts.args[-1]

    rows, pct = load_rows(opts.args[0], opts.symbol, opts.objects)
    kinds, moves = analyse(rows)
    count = Counter(k for k in kinds if k and k not in ("pool", "branch"))
    print(f"{opts.symbol}: {pct:.2f} %" if pct is not None else opts.symbol)
    print("rows: " + (", ".join(f"{k} {n}" for k, n in count.most_common()) or "no difference"))

    pairs, lines = permutation(rows, kinds)
    # Each of our registers maps to the original register it pairs with most.
    best = {}
    for (x, y), n in sorted(pairs.items(), key=lambda kv: -kv[1]):
        if x not in best:
            best[x] = (y, n, pairs[(x, x)])
    perm = {x: y for x, (y, n, same) in best.items() if x != y and n > same}
    if perm:
        print("\nregister permutation (ours -> original), with our source lines:")
        for x in sorted(perm, key=lambda r: int(r[1:]) if r[1:].isdigit() else 99):
            y = perm[x]
            ls = sorted(lines[(x, y)])
            shown = ", ".join(map(str, ls[:12])) + (" ..." if len(ls) > 12 else "")
            print(f"  {x} -> {y}  ({pairs[(x, y)]} uses; lines {shown})")
        for cyc in cycles(perm):
            kind = "callee-saved" if set(cyc) <= CALLEE else "mixed"
            print("  cycle " + " -> ".join(cyc + [cyc[0]]) + f"  [{kind}]")

    stack = Counter()
    stack_lines = defaultdict(set)
    for row, k in zip(rows, kinds):
        if k == "stack":
            oa = re.findall(r"#(-?0x[0-9a-f]+|-?\d+)", row["orig"])
            ob = re.findall(r"#(-?0x[0-9a-f]+|-?\d+)", row["ours"])
            if len(oa) == len(ob):
                for x, y in zip(ob, oa):
                    if x != y:
                        stack[(x, y)] += 1
                        if row["line"]:
                            stack_lines[(x, y)].add(row["line"])
    if stack:
        print("\nstack offsets (ours -> original):")
        for (x, y), n in stack.most_common(12):
            print(f"  sp+{x} -> sp+{y}  ({n} rows; lines {', '.join(map(str, sorted(stack_lines[(x, y)])[:8]))})")

    if moves:
        print("\nmoved instructions (scheduling): original row -> our row")
        for i, j in moves[:20]:
            print(f"  {rows[i]['orig']:<40} row {i} -> {j} (line {rows[j]['line']})")

    real = [(i, k) for i, k in enumerate(kinds) if k in ("extra", "missing", "other")]
    if real:
        print("\ncode differences:")
        for i, k in real[:20]:
            r = rows[i]
            print(f"  row {i:4} {k:7} orig: {r['orig']:<40} ours: {r['ours']:<40} line {r['line']}")

    if opts.rows:
        print("\nrows:")
        for i, (r, k) in enumerate(zip(rows, kinds)):
            if k and k not in ("pool", "branch"):
                print(f"  {i:4} {k:8} {r['orig']:<40} | {r['ours']:<40} line {r['line']}")


if __name__ == "__main__":
    main()
