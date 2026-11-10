#!/usr/bin/env python3
"""Call-graph density of .text: how self-contained each address window is.

Builds the direct call graph (ARM BL/BLX imm, Thumb BL/BLX) between the functions of
symbols.txt, then prints, for each window, the share of calls made from the window
that stay inside it. A prebuilt library calls itself much more than game code does
(game code calls everything), so library blocks stand out as plateaus. --core gives
an address range instead: each group of functions is scored by the share of its
call links (callers and callees) inside that range, to find the block's edges.

Usage:
  python tools/link_density.py                        # 128 KiB windows, 64 KiB step
  python tools/link_density.py --window 0x20000 --step 0x10000
  python tools/link_density.py --core 0x3F0000-0x4C0000 --range 0x3C0000-0x500000
"""

import argparse
import bisect
import collections
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYM = re.compile(r"(\S+) = \.text:0x([0-9A-Fa-f]+); // type:function size:0x([0-9A-Fa-f]+)(.*)")
TEXT = 0x00100000


def load(version):
    data = (ROOT / "orig" / version / "code.bin").read_bytes()
    syms = []
    for line in (ROOT / "config" / version / "symbols.txt").read_text(encoding="utf-8").splitlines():
        m = SYM.match(line)
        if m:
            syms.append((int(m[2], 16), int(m[3], 16), "mode:thumb" in m[4]))
    syms.sort()
    return data, syms


def call_graph(data, syms, text_end):
    callees = collections.defaultdict(set)
    for addr, size, thumb in syms:
        if not thumb:
            for pc in range(addr, addr + size - 3, 4):
                w = struct.unpack_from("<I", data, pc - TEXT)[0]
                if (w >> 24) == 0xEB or (w >> 25) == 0x7D:  # BL, BLX imm
                    off = w & 0xFFFFFF
                    off -= 0x1000000 if off & 0x800000 else 0
                    target = pc + 8 + off * 4
                    if (w >> 25) == 0x7D:
                        target += ((w >> 24) & 1) * 2
                    if TEXT <= target < text_end:
                        callees[addr].add(target)
        else:
            pc = addr
            while pc < addr + size - 2:
                h1, h2 = struct.unpack_from("<HH", data, pc - TEXT)
                if (h1 >> 11) == 0x1E and (h2 >> 11) in (0x1F, 0x1D):  # BL, BLX
                    off = ((h1 & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
                    off -= 0x800000 if off & 0x400000 else 0
                    target = pc + 4 + off
                    if (h2 >> 11) == 0x1D:
                        target &= ~3
                    if TEXT <= target < text_end:
                        callees[addr].add(target)
                    pc += 4
                else:
                    pc += 2
    return callees


def span(text):
    lo, hi = text.split("-")
    return int(lo, 16), int(hi, 16)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", default="jpn")
    parser.add_argument("--window", type=lambda s: int(s, 0), default=0x20000)
    parser.add_argument("--step", type=lambda s: int(s, 0), default=0x10000)
    parser.add_argument("--core", type=span, help="lo-hi: score functions by links into this range")
    parser.add_argument("--range", type=span, help="lo-hi: functions to score with --core")
    parser.add_argument("--group", type=int, default=24, help="functions per line with --core")
    args = parser.parse_args()

    data, syms = load(args.version)
    text_end = TEXT + len(data)  # bounded by the targets that are functions anyway
    starts = {s[0] for s in syms}
    callees = call_graph(data, syms, text_end)
    for f in callees:
        callees[f] &= starts

    if args.core:
        clo, chi = args.core
        lo, hi = args.range or (clo, chi)
        callers = collections.defaultdict(set)
        for f, ts in callees.items():
            for t in ts:
                callers[t].add(f)
        funcs = [s[0] for s in syms if lo <= s[0] < hi]
        for i in range(0, len(funcs), args.group):
            group = funcs[i:i + args.group]
            inside = total = 0
            for f in group:
                links = (callees.get(f, set()) | callers.get(f, set())) - {f}
                inside += sum(1 for x in links if clo <= x < chi)
                total += len(links)
            print(f"0x{group[0]:08X}-0x{group[-1]:08X} links into core {inside:4}/{total:4} "
                  f"{inside / max(total, 1):.2f}")
        return

    last = max(s[0] for s in syms)
    for lo in range(TEXT, last, args.step):
        hi = lo + args.window
        inside = outside = 0
        for f, ts in callees.items():
            if lo <= f < hi:
                for t in ts:
                    if lo <= t < hi:
                        inside += 1
                    else:
                        outside += 1
        share = inside / max(inside + outside, 1)
        print(f"0x{lo:08X} {share:.2f} {inside + outside:5} " + "#" * int(share * 50))


if __name__ == "__main__":
    main()
