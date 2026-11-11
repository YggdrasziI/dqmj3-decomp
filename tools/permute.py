#!/usr/bin/env python3
"""Search source forms of one function until its compiled bytes equal the original.

A heuristic: the function's body is mutated at random (statement order, declaration
placement, scopes, copies of locals, operand order, loop counter types), every variant
is compiled with armcc exactly as the build compiles the unit, and the variants closest
to the original are kept. The mutations come from DQMJ2's search for mwccarm, whose
register allocation depends on declaration order, scopes and copies; armcc (RVCT 4.1)
allocates registers differently, and which source changes move its output is not
established, so a search can find nothing even when a match exists.

Variants live in a temporary directory: the repository is never written. A result
counts only when the bytes equal the target (`score` 0), and then
`python tools/report_diff.py` and `ninja` remain the proof. The output form is a
compiler fact, not evidence of the original source.

  python tools/permute.py <unit> <symbol> [--seconds N] [--workers N] [--out DIR]
  python tools/permute.py game/FieldScriptFunc _Z14SetFogDensity_P4SQVM --seconds 20

<unit> is the objdiff unit name (objdiff.json). The compile command (armcc and
`cflags`) is read from the unit's edge in build.ninja (compile_commands.json holds
clang flags for clangd, not armcc's); include paths are made absolute and the
directory of the original source is searched first, so the variant compiles from a
temporary copy at the same relative path. Each variant then goes through
tools/ctr/prelink.py (armlink's call inlining, as for objdiff) and is compared with
build/<version>/delink/<unit>.o: by objdiff's match percent (default), or with
--scorer words by differing instruction words, where a relocated word is compared by
its target (and the condition and opcode bits of a branch, the addend of an absolute
word) instead of its bytes.

With 0 reached, mutations that are not needed are reverted and the function, from its
signature to its closing brace, is written to <out>/<symbol>.txt after a line naming the
source file. Without a match, the closest form is written to <out>/<symbol>.best.txt.

DQMJ2's mutations that read an expression into a new local declare it with
`__typeof__`, which armcc 4.1 rejects with this project's flags (no GNU mode), so they
are not used here.
"""
import argparse
import difflib
import json
import os
import random
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from ctr import elf  # noqa: E402
from ctr.prelink import load_context, prepare_object  # noqa: E402
from ctr.symbols import Splits  # noqa: E402
from ctr.units import object_name  # noqa: E402

OBJDIFF = os.path.join(ROOT, "build", "tools", "objdiff-cli.exe" if os.name == "nt" else "objdiff-cli")
FAIL = 10**6


###
# Build data
###

def ninja_edge(output):
    """Variables of the build.ninja edge that produces `output` (a path with '/')."""
    text = open(os.path.join(ROOT, "build.ninja"), encoding="utf-8").read()
    text = re.sub(r"\$\n\s*", "", text)  # join continuation lines
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("build ") and line[6:].split(":")[0].split() and \
                line[6:].split(":")[0].split()[0] == output:
            rule = line.split(":", 1)[1].split()[0]
            vars_ = {"rule": rule}
            for var in lines[i + 1:]:
                m = re.match(r"^\s+(\w+)\s*=\s*(.*)$", var)
                if not m:
                    break
                vars_[m.group(1)] = m.group(2).replace("$$", "$")
            return vars_
    return None


def compile_command(edge):
    """armcc (native path) and its flags, with -I/-J paths made absolute."""
    cc = os.path.normpath(os.path.join(ROOT, edge["armcc"]))
    flags = []
    for f in edge["cflags"].split():
        if f[:2] in ("-I", "-J") and len(f) > 2 and not os.path.isabs(f[2:]):
            f = f[:2] + os.path.normpath(os.path.join(ROOT, f[2:]))
        flags.append(f)
    return cc, flags


###
# Objects
###

def reloc_target(obj, section, reloc):
    """What a relocation refers to, independent of where the word is: the symbol name
    (a section symbol by its section's name), with the addend of an absolute word or
    the condition and opcode bits of an ARM branch."""
    sym = obj.symbols[reloc.symbol]
    name = sym.name
    if not name and sym.type == elf.STT_SECTION and 0 < sym.shndx < len(obj.sections):
        name = obj.sections[sym.shndx].name
    word = struct.unpack_from("<I", section.data, reloc.offset)[0] if reloc.offset + 4 <= len(section.data) else 0
    if reloc.type in (elf.R_ARM_ABS32, elf.R_ARM_TARGET1, elf.R_ARM_REL32):
        return (name, word)
    if reloc.type in (elf.R_ARM_CALL, elf.R_ARM_JUMP24, elf.R_ARM_PC24):
        return (name, word & 0xFF000000)
    return (name, None)


def elf_func(path, name):
    """(bytes, {offset: target}, thumb) of a function symbol, or (None, None, False)."""
    obj = elf.ElfFile.load(Path(path))
    for sym in obj.symbols:
        if sym.name == name and sym.type == elf.STT_FUNC and 0 < sym.shndx < len(obj.sections):
            section = obj.sections[sym.shndx]
            start = sym.value & ~1
            data = section.data[start:start + sym.size]
            rel = {r.offset - start: reloc_target(obj, section, r)
                   for r in section.relocs if start <= r.offset < start + sym.size}
            return data, rel, bool(sym.value & 1)
    return None, None, False


def score(path, name, tgt, trel, thumb):
    """Differing words (halfwords in Thumb code); a relocated word counts by its target."""
    d, rel, _ = elf_func(path, name)
    if d is None:
        return FAIL
    if len(d) != len(tgt):
        return 5000 + abs(len(d) - len(tgt))
    masked = {o + k for o in set(rel) | set(trel) for k in range(1, 4)}
    n = 0
    for i in range(0, len(tgt), 2 if thumb else 4):
        if i in trel or i in rel:
            if trel.get(i) != rel.get(i):
                n += 1
        elif i not in masked and d[i:i + 4] != tgt[i:i + 4]:
            n += 1
    return n


def objdiff_score(target, ob, symbol, js):
    """100 minus objdiff's match percent of the function (0: a match), as in the report."""
    if os.path.exists(js):
        os.remove(js)
    r = subprocess.run([OBJDIFF, "diff", "-1", target, "-2", ob, symbol, "-o", js, "--format", "json"],
                       capture_output=True)
    if r.returncode or not os.path.exists(js):
        return None
    with open(js, encoding="utf-8") as f:
        d = json.load(f)
    for s in d.get("right", {}).get("symbols", []):
        if s.get("name") == symbol and s.get("match_percent") is not None:
            return 0 if s["match_percent"] >= 100 else 100 - s["match_percent"]
    return None


###
# Mutations (from DQMJ2's tools/permute.py)
###

WRITE = re.compile(r"^\s*(?:[\w:<>]+[\s*&]+)*(\w+)\s*(?:[-+*/|&^]|<<|>>)?=(?!=)")


def depends(a, b):
    """True if two statements cannot be swapped: one writes a local the other uses."""
    for x, y in ((a, b), (b, a)):
        m = WRITE.match(x)
        if m and re.search(r"\b%s\b" % re.escape(m.group(1)), y):
            return True
    return False


DECL = re.compile(r"^(\s*)((?:const\s+)?(?:unsigned\s+)?[A-Za-z_]\w*(?:\s*\*+\s*|\s+)(?:const\s+)?)([a-z_A-Z]\w*)(\s*=\s*(.*))?;\s*$")
KW = {"return", "goto", "delete", "else", "case", "break", "continue", "new"}


def is_decl(l):
    m = DECL.match(l)
    return m if m and m.group(2).split()[0] not in KW else None


def block_end(L, i):
    return not L[i].rstrip().endswith("{") and not L[i].strip().startswith("}")


COUNTER = re.compile(r"for \((int|unsigned int) (\w+) = ([^;]+); (\(int\))?\2 (<=?) ")


def counter_type(L):
    """Cycle a loop counter through `int i; i <`, `unsigned int i; (int)i <` and
    `unsigned int i; i <` (also `<=`)."""
    c = [i for i, l in enumerate(L) if COUNTER.search(l)]
    if not c:
        return L
    i = random.choice(c)
    m = COUNTER.search(L[i])
    forms = ["for (int {0} = {1}; {0} {2} ", "for (unsigned int {0} = {1}; (int){0} {2} ",
             "for (unsigned int {0} = {1}; {0} {2} "]
    cur = 0 if m.group(1) == "int" else (1 if m.group(4) else 2)
    new = random.choice([f for j, f in enumerate(forms) if j != cur]).format(m.group(2), m.group(3), m.group(5))
    L[i] = L[i][: m.start()] + new + L[i][m.end() :]
    return L


def l_has(L, name):
    return re.search(r"\b%s\b" % re.escape(name), "\n".join(L)) is not None


FOCUS = None  # (texts of the body lines near a difference, texts of all body lines); None: all


def in_focus(line):
    """A line may be mutated: near a difference (--focus), or inserted by a mutation."""
    return FOCUS is None or line in FOCUS[0] or line not in FOCUS[1]


def scope_block(L):
    """Put one or two consecutive simple statements in their own { } block."""
    c = [i for i, l in enumerate(L) if l.strip().endswith(";") and block_end(L, i) and in_focus(l)
         and not re.match(r"^\s*(case|default|return|break)\b", l)]
    if not c:
        return L
    i = random.choice(c)
    j = i
    if i + 1 < len(L) and L[i + 1].strip().endswith(";") and block_end(L, i + 1) and random.random() < 0.5:
        j = i + 1
    ind = re.match(r"^(\s*)", L[i]).group(1)
    return L[:i] + [ind + "{"] + ["    " + x for x in L[i : j + 1]] + [ind + "}"] + L[j + 1 :]


def mutate(L):
    L = list(L)
    idx = [i for i in range(len(L)) if in_focus(L[i])]
    if random.random() < 0.06:  # statements in their own scope
        R = scope_block(list(L))
        if R != L:
            return R
    if random.random() < 0.05:  # loop counter type
        R = counter_type(list(L))
        if R != L:
            return R
    k = random.random()
    if k < 0.28:  # swap adjacent simple statements
        c = [i for i in idx if i + 1 < len(L) and block_end(L, i) and block_end(L, i + 1) and L[i].strip().endswith(";") and L[i + 1].strip().endswith(";")
             and not depends(L[i], L[i + 1])]
        if c:
            i = random.choice(c)
            L[i], L[i + 1] = L[i + 1], L[i]
    elif k < 0.48:  # move a declaration without initializer anywhere above its use
        c = [i for i in idx if is_decl(L[i]) and not is_decl(L[i]).group(4)]
        if c:
            i = random.choice(c)
            l = L.pop(i)
            L.insert(random.randrange(0, min(i + 3, len(L))), l)
    elif k < 0.66:  # split `T x = e;` into a declaration at the top and an assignment
        c = [i for i in idx if is_decl(L[i]) and is_decl(L[i]).group(4)]
        if c:
            i = random.choice(c)
            m = is_decl(L[i])
            L[i] = "%s%s = %s;" % (m.group(1), m.group(3), m.group(5))
            L.insert(random.randrange(0, 4) if len(L) > 4 else 0, "    %s%s;" % (m.group(2).replace("const ", ""), m.group(3)))
    elif k < 0.76:  # add or drop const on an initialised local
        c = [i for i in idx if is_decl(L[i]) and is_decl(L[i]).group(4)]
        if c:
            i = random.choice(c)
            L[i] = L[i].replace("const ", "", 1) if "const " in L[i] else re.sub(r"^(\s*)", r"\1const ", L[i], count=1)
    elif k < 0.88:  # commute an operator
        c = [i for i in idx if re.search(r"\S+ (==|!=|\+|\*|&|\|) \S+", L[i])]
        if c:
            i = random.choice(c)
            ms = list(re.finditer(r"([\w\->\.\[\]]+) (==|!=|\+|\*|&|\|) ([\w\->\.\[\]]+)", L[i]))
            if ms:
                m = random.choice(ms)
                L[i] = L[i][: m.start()] + m.group(3) + " " + m.group(2) + " " + m.group(1) + L[i][m.end() :]
    elif k < 0.95:  # a copy of a local: `T y = x;` right after its declaration, then use y
        c = [i for i in idx if is_decl(L[i]) and is_decl(L[i]).group(4)]
        if c:
            i = random.choice(c)
            m = is_decl(L[i])
            n = m.group(3)
            nn = n + "_"
            if not l_has(L, nn):
                L.insert(i + 1, "%s%s%s = %s;" % (m.group(1), m.group(2), nn, n))
                for j in range(i + 2, len(L)):
                    if random.random() < 0.7:
                        L[j] = re.sub(r"\b%s\b" % n, nn, L[j])
    else:  # compound assignment split `x += e;` <-> `x = x + e;`
        c = [i for i in idx if re.search(r"^\s*\w+ [-+|&]= ", L[i])]
        if c:
            i = random.choice(c)
            m = re.match(r"^(\s*)(\w+) ([-+|&])= (.*);", L[i])
            if m:
                L[i] = "%s%s = %s %s %s;" % (m.group(1), m.group(2), m.group(2), m.group(3), m.group(4))
    return L


def locate(symbol):
    """Regex for the definition of a mangled or plain symbol, written from column 0
    (not in a // comment, not a call in a condition or a return)."""
    # A definition starts at column 0; a line with a control keyword is a call site
    head = r"^(?![ \t]|//)(?![^\n]*\b(?:if|while|for|switch|return)\b)[^\n;#]*\b"
    f = re.match(r"_Z(\d+)", symbol)
    if f:  # free function: _Z<length><name><parameters>
        name = symbol[f.end() : f.end() + int(f.group(1))]
        return head + r"%s\([^;{]*\{\n" % re.escape(name)
    m = re.match(r"_ZNK?(\d+)", symbol)
    if not m:
        return head + r"%s\([^;{]*\{\n" % re.escape(symbol)
    p = m.end(1)
    n = int(m.group(1))
    cls = symbol[p : p + n]
    rest = symbol[p + n :]
    c = re.match(r"(C|D)[0-9]", rest)
    if c:
        name = cls if c.group(1) == "C" else "~" + cls
    else:
        q = re.match(r"(\d+)", rest)
        if not q:
            return None
        name = rest[q.end() : q.end() + int(q.group(1))]
    return head + r"%s::%s\([^;{]*\{\n" % (cls, re.escape(name))


def locate_in_class(symbol, text):
    """Match of the definition of a method written in its class body (indented, without
    `Class::`), searched within the body of `class|struct <Class>`."""
    m = re.match(r"_ZNK?(\d+)", symbol)
    if not m:
        return None
    p = m.end(1)
    cls = symbol[p : p + int(m.group(1))]
    rest = symbol[p + int(m.group(1)) :]
    c = re.match(r"(C|D)[0-9]", rest)
    if c:
        name = cls if c.group(1) == "C" else "~" + cls
    else:
        q = re.match(r"(\d+)", rest)
        if not q:
            return None
        name = rest[q.end() : q.end() + int(q.group(1))]
    k = re.search(r"^(?:class|struct)\s+%s\b[^;{]*\{" % re.escape(cls), text, re.M)
    if not k:
        return None
    end = body_end(text, k.end()) or len(text)
    # Indented, not a comment, a call in a condition or an assignment
    head = r"^[ \t]+(?!//)(?![^\n]*\b(?:if|while|for|switch|return)\b)[^\n;#=(]*"
    rx = re.compile(head + r"(?<![\w~])%s\([^;{]*\{\n" % re.escape(name), re.M)
    return rx.search(text, k.end(), end)


def body_end(text, start):
    """Index just after the newline that follows the brace closing the body opened
    right before `start`; braces in comments, strings and characters do not count."""
    depth, i, n = 1, start, len(text)
    while i < n:
        c = text[i]
        if text.startswith("//", i):
            i = text.find("\n", i)
            if i < 0:
                return None
        elif text.startswith("/*", i):
            i = text.find("*/", i + 2)
            if i < 0:
                return None
            i += 1
        elif c in "\"'":
            j = i + 1
            while j < n and text[j] != c:
                j += 2 if text[j] == "\\" else 1
            i = j
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                nl = text.find("\n", i)
                return n if nl < 0 else nl + 1
        i += 1
    return None


def diff_lines(unit, symbol):
    """Our source lines of the differing instructions (tools/why_diff.py's row kinds)."""
    import why_diff
    rows, _ = why_diff.load_rows(unit, symbol)
    kinds, _ = why_diff.analyse(rows)
    return {r["line"] for r, k in zip(rows, kinds) if r["line"] and k not in (None, "pool", "branch")}


###
# Search
###

class Search:
    """Compiles variants of one function and scores them. With `target` (the split
    object), the score is objdiff's (100 minus the match percent, times `scale`);
    without it, the count of differing words (score())."""

    def __init__(self, pre, post, src_rel, cc, flags, ctx, unit, symbol, tgt, trel, thumb, tmp,
                 workers, target=None, scale=1.0):
        self.pre, self.post, self.src_rel, self.symbol = pre, post, src_rel, symbol
        self.cc, self.flags, self.ctx, self.unit = cc, flags, ctx, unit
        self.tgt, self.trel, self.thumb, self.tmp = tgt, trel, thumb, tmp
        self.target, self.scale = target, scale
        self.ex = ThreadPoolExecutor(workers)
        self.workers = workers
        self.lock = threading.Lock()  # prelink shares the link context
        self.error = None

    def run(self, i, lines):
        work = os.path.join(self.tmp, "v%d" % i)
        c = os.path.join(work, self.src_rel)
        ob = os.path.join(work, "v.o")
        pre = os.path.join(work, "v.diff.o")
        os.makedirs(os.path.dirname(c), exist_ok=True)
        with open(c, "w", encoding="utf-8", errors="surrogateescape", newline="\n") as f:
            f.write(self.pre + "\n".join(lines) + "\n" + self.post)
        for p in (ob, pre):
            if os.path.exists(p):
                os.remove(p)
        # A list, not a shell string: no shell or MSYS path conversion touches the
        # flags (e.g. --apcs=/interwork); cwd is the variant's root so the source path
        # (and __FILE__) is the same relative path as in the build.
        try:
            r = subprocess.run([self.cc] + self.flags + ["-c", self.src_rel, "-o", ob],
                               capture_output=True, text=True, cwd=work, timeout=120)
        except subprocess.TimeoutExpired:
            return FAIL
        if r.returncode or not os.path.exists(ob):
            self.error = (r.stdout + r.stderr).strip()
            return FAIL
        try:
            with self.lock:
                prepare_object(self.ctx, Path(ob), Path(pre), self.unit)
        except Exception as e:  # a variant the prelink step rejects
            self.error = "prelink: %s" % e
            return FAIL
        if self.target:
            v = objdiff_score(self.target, pre, self.symbol, os.path.join(work, "v.json"))
            return FAIL if v is None else v * self.scale
        return score(pre, self.symbol, self.tgt, self.trel, self.thumb)

    def batch(self, C):
        return list(self.ex.map(self.run, range(len(C)), C))


def cleanup(s, body, L, goal=0):
    """Revert every difference from the original body that a score of `goal` does not need
    (0: the match; the best score for a closest form)."""
    changed = True
    while changed:
        changed = False
        ops = [o for o in difflib.SequenceMatcher(None, body, L, autojunk=False).get_opcodes() if o[0] != "equal"]
        C = [L[: o[3]] + body[o[1] : o[2]] + L[o[4] :] for o in ops]
        for k in range(0, len(C), s.workers):
            part = C[k : k + s.workers]
            R = s.batch(part)
            ok = [x for r, x in zip(R, part) if r <= goal]
            if ok:
                L = min(ok, key=lambda x: sum(a != b for a, b in zip(x, body)))
                changed = True
                break
    return L


def main():
    a = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    a.add_argument("unit", help="objdiff unit name, e.g. game/FieldScriptFunc")
    a.add_argument("symbol")
    a.add_argument("--version", default="jpn")
    a.add_argument("--seconds", type=int, default=60)
    a.add_argument("--workers", type=int, default=min(16, os.cpu_count() or 4))
    a.add_argument("--out", default=None)
    a.add_argument("--scorer", choices=("objdiff", "words"), default="objdiff",
                   help="objdiff: the report's match percent (default); words: differing words, faster")
    a.add_argument("--focus", type=int, default=None, metavar="N",
                   help="mutate only lines within N lines of a difference (needs line information "
                        "in the object, which armcc only emits with -g)")
    o = a.parse_args()
    os.chdir(ROOT)

    with open("objdiff.json", encoding="utf-8") as f:
        units = {u["name"]: u for u in json.load(f)["units"]}
    if o.unit not in units:
        sys.exit("unit not in objdiff.json: " + o.unit)
    meta = units[o.unit].get("metadata", {})
    src = meta.get("source_path")
    if not src or not os.path.exists(src):
        sys.exit("unit has no source file: " + o.unit)
    target = units[o.unit]["target_path"]
    if not os.path.exists(target):
        sys.exit(target + " is missing: run ninja first")
    edge = ninja_edge("build/%s/src/%s.o" % (o.version, o.unit))
    if not edge or "armcc" not in edge or "cflags" not in edge:
        sys.exit("no armcc edge for the unit in build.ninja: run python configure.py")
    cc, flags = compile_command(edge)
    flags = ["-I" + os.path.abspath(os.path.dirname(src))] + flags

    config_path = Path("config") / o.version / "config.toml"
    config, ctx = load_context(config_path)
    splits = Splits.load(config.splits_path)
    split_unit = next((u for u in splits.units if object_name(u) == o.unit + ".o"), None)
    if split_unit is None:
        sys.exit("unit not in splits.txt: " + o.unit)

    tgt, trel, thumb = elf_func(target, o.symbol)
    if tgt is None:
        sys.exit("symbol not in target: " + o.symbol)
    raw = open(src, "rb").read().decode("utf-8", errors="surrogateescape")
    text = raw.replace("\r\n", "\n")
    rx = locate(o.symbol)
    m = re.search(rx, text, re.M) if rx else None
    if not m:
        m = locate_in_class(o.symbol, text)
    if not m:
        sys.exit("definition not found: " + o.symbol)
    s0 = m.end()
    e = body_end(text, s0)
    if e is None:
        sys.exit("end of the definition not found: " + o.symbol)
    pre, body, post = text[:s0], text[s0:e].split("\n")[:-1], text[e:]
    if o.focus is not None:
        global FOCUS
        first = pre.count("\n") + 1  # file line of body[0]
        near = {i for ln in diff_lines(o.unit, o.symbol) for i in range(len(body)) if abs(first + i - ln) <= o.focus}
        if near:
            FOCUS = ({body[i] for i in near}, set(body))
            print("focus:", len(near), "of", len(body), "lines", flush=True)
        else:
            print("focus: no line information, every line may be mutated", flush=True)
    tmp = tempfile.mkdtemp(prefix="perm_")
    try:
        # objdiff's percent scaled to words, so the search thresholds keep their meaning
        target_o = os.path.abspath(target) if o.scorer == "objdiff" else None
        s = Search(pre, post, src, cc, flags, ctx, split_unit, o.symbol, tgt, trel, thumb, tmp, o.workers,
                   target_o, len(tgt) / 400.0)
        best = cur = start = s.run(0, body)
        if start >= FAIL:
            sys.exit("the unmodified source does not compile or prelink:\n%s" % s.error)
        print("start", round(start, 3), "of", len(tgt) // 4, flush=True)
        bestL = curL = body
        t0 = time.time()
        n = 0
        while time.time() - t0 < o.seconds and best > 0:
            C = []
            for _ in range(o.workers):
                L = curL
                for _ in range(random.choice((1, 1, 2, 3))):
                    L = mutate(L)
                C.append(L)
            R = s.batch(C)
            n += len(C)
            v, L = min(zip(R, C), key=lambda x: x[0])
            if v < 5000 and (v <= cur or random.random() < 0.015):
                cur, curL = v, L
            if v < best:
                best, bestL = v, L
                print(round(time.time() - t0), n, "best", round(best, 3), flush=True)
            if cur > best + 6:
                cur, curL = best, bestL
        print("done", n, "variants, best", round(best, 3), flush=True)
        if 0 < best < start and o.out:  # not a match: keep the closest form for the next run
            bestL = cleanup(s, body, bestL, best)
            os.makedirs(o.out, exist_ok=True)
            with open(os.path.join(o.out, o.symbol + ".best.txt"), "w", encoding="utf-8",
                      errors="surrogateescape", newline="\n") as f:
                f.write("%s score %s (start %s)\n%s\n%s\n}\n" % (src, round(best, 3), round(start, 3), m.group(0).rstrip("\n"), "\n".join(bestL)))
        if best == 0 and o.out:
            bestL = cleanup(s, body, bestL)
            os.makedirs(o.out, exist_ok=True)
            with open(os.path.join(o.out, o.symbol + ".txt"), "w", encoding="utf-8",
                      errors="surrogateescape", newline="\n") as f:
                f.write(src + "\n" + m.group(0).rstrip("\n") + "\n" + "\n".join(bestL) + "\n}\n")
        s.ex.shutdown()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0 if best == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
