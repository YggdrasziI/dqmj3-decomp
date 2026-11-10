"""
symbols.txt and splits.txt

Both files use the same line-oriented format as decomp-toolkit projects so they are
familiar to edit, with two additions that the ARM toolchain needs:

  - function symbols may carry `mode:thumb`
  - a function symbol without a size is a second name for the function at the same
    address (the compiler emits constructors and destructors under two names)
  - a unit in splits.txt may list the same section more than once, because armlink
    orders code by section name and so the functions of one source file are usually
    not contiguous in the image

symbols.txt:
    <name> = <section>:0x<address>; // type:<function|object|label> size:0x<size> scope:<global|local|weak> [mode:thumb]

splits.txt:
    Sections:
    \t<section>  type:<code|rodata|data|bss> align:<n>

    <path/to/unit.cpp>:
    \t<section>  start:0x<address> end:0x<address>
"""

import bisect
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

SYMBOL_RE = re.compile(
    r"^\s*(?P<name>\S+)\s*=\s*(?P<section>[^:\s]+):0x(?P<addr>[0-9A-Fa-f]+);"
    r"(?:\s*//\s*(?P<attrs>.*))?$"
)

TYPE_FUNCTION = "function"
TYPE_OBJECT = "object"
TYPE_LABEL = "label"


@dataclass
class Symbol:
    name: str
    section: str
    address: int
    type: str = TYPE_LABEL
    size: int = 0
    scope: str = "global"
    thumb: bool = False
    # Attributes this tooling does not interpret are kept verbatim
    extra: Dict[str, str] = field(default_factory=dict)

    @property
    def end(self) -> int:
        return self.address + self.size

    @property
    def is_function(self) -> bool:
        return self.type == TYPE_FUNCTION

    def format(self) -> str:
        attrs = [f"type:{self.type}"]
        if self.size:
            attrs.append(f"size:0x{self.size:X}")
        attrs.append(f"scope:{self.scope}")
        if self.thumb:
            attrs.append("mode:thumb")
        for key, value in self.extra.items():
            attrs.append(f"{key}:{value}" if value else key)
        return f"{self.name} = {self.section}:0x{self.address:08X}; // {' '.join(attrs)}"


def parse_symbol(line: str, where: str = "") -> Optional[Symbol]:
    stripped = line.strip()
    if not stripped or stripped.startswith("//") or stripped.startswith("#"):
        return None
    m = SYMBOL_RE.match(line)
    if m is None:
        raise ValueError(f"{where}: malformed symbol line: {line.rstrip()}")
    sym = Symbol(m["name"], m["section"], int(m["addr"], 16))
    for attr in (m["attrs"] or "").split():
        key, _, value = attr.partition(":")
        if key == "type":
            sym.type = value
        elif key == "size":
            sym.size = int(value, 16)
        elif key == "scope":
            sym.scope = value
        elif key == "mode":
            sym.thumb = value == "thumb"
        else:
            sym.extra[key] = value
    return sym


class SymbolTable:
    def __init__(self, symbols: Iterable[Symbol] = ()) -> None:
        self.symbols: List[Symbol] = sorted(symbols, key=lambda s: (s.address, s.name))
        self._addresses: List[int] = [s.address for s in self.symbols]
        self.by_name: Dict[str, List[Symbol]] = {}
        for sym in self.symbols:
            self.by_name.setdefault(sym.name, []).append(sym)

    @staticmethod
    def load(path: Path) -> "SymbolTable":
        symbols = []
        with open(path, "r", encoding="utf-8") as f:
            for num, line in enumerate(f, 1):
                sym = parse_symbol(line, f"{path}:{num}")
                if sym is not None:
                    symbols.append(sym)
        return SymbolTable(symbols)

    def save(self, path: Path) -> None:
        # Use the same ordering as load, including aliases appended during registration.
        content = "".join(sym.format() + "\n" for sym in
                          sorted(self.symbols, key=lambda s: (s.address, s.name)))
        # Registration often claims already-named functions. Keep the timestamp
        # unchanged in that case so Ninja need not prelink every existing unit.
        if path.exists() and path.read_text(encoding="utf-8") == content:
            return
        # Readers also run in parallel workers. Publish the whole table at once
        # so they never parse a truncated or partially written registration.
        import os
        import stat
        import tempfile
        fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            if path.exists():
                os.chmod(temporary, stat.S_IMODE(path.stat().st_mode))
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def __iter__(self) -> Iterator[Symbol]:
        return iter(self.symbols)

    def __len__(self) -> int:
        return len(self.symbols)

    def at(self, addr: int) -> List[Symbol]:
        """All symbols defined exactly at `addr`."""
        i = bisect.bisect_left(self._addresses, addr)
        result = []
        while i < len(self.symbols) and self.symbols[i].address == addr:
            result.append(self.symbols[i])
            i += 1
        return result

    def first_at(self, addr: int) -> Optional[Symbol]:
        syms = self.at(addr)
        if not syms:
            return None
        # Prefer the symbol that carries a size (functions/objects over plain labels)
        return max(syms, key=lambda s: (s.size > 0, s.type != TYPE_LABEL))

    def containing(self, addr: int) -> Optional[Symbol]:
        """The sized symbol whose range covers `addr`, or a symbol exactly at `addr`."""
        exact = self.first_at(addr)
        if exact is not None:
            return exact
        i = bisect.bisect_right(self._addresses, addr) - 1
        while i >= 0:
            sym = self.symbols[i]
            if sym.address <= addr < sym.end:
                return sym
            # Sized symbols do not nest, so the first candidate that ends before
            # `addr` rules out everything earlier.
            if sym.size and sym.end <= addr:
                return None
            i -= 1
        return None

    def in_range(self, start: int, end: int) -> List[Symbol]:
        lo = bisect.bisect_left(self._addresses, start)
        hi = bisect.bisect_left(self._addresses, end)
        return self.symbols[lo:hi]

    def find(self, name: str) -> List[Symbol]:
        return self.by_name.get(name, [])


###
# splits.txt
###


@dataclass
class SplitRange:
    section: str
    start: int
    end: int

    def contains(self, addr: int) -> bool:
        return self.start <= addr < self.end


@dataclass
class Unit:
    name: str  # source path relative to src/, e.g. "game/Foo.cpp"
    ranges: List[SplitRange] = field(default_factory=list)
    auto: bool = False  # generated for space no source file claims
    category: Optional[str] = None  # library an automatic unit is attributed to

    def ranges_in(self, section: str) -> List[SplitRange]:
        return [r for r in self.ranges if r.section == section]

    def contains(self, addr: int) -> bool:
        return any(r.contains(addr) for r in self.ranges)


@dataclass
class SectionDef:
    name: str
    kind: str
    align: int = 4


class Splits:
    def __init__(self) -> None:
        self.sections: List[SectionDef] = []
        self.units: List[Unit] = []

    @staticmethod
    def load(path: Path) -> "Splits":
        splits = Splits()
        current: Optional[Unit] = None
        in_sections = False
        with open(path, "r", encoding="utf-8") as f:
            for num, raw in enumerate(f, 1):
                line = raw.split("//")[0].rstrip()
                if not line.strip():
                    continue
                where = f"{path}:{num}"
                if not line[0].isspace():
                    if not line.endswith(":"):
                        raise ValueError(f"{where}: expected '<name>:'")
                    name = line[:-1].strip()
                    if name == "Sections":
                        in_sections = True
                        current = None
                    else:
                        in_sections = False
                        current = Unit(name)
                        splits.units.append(current)
                    continue
                parts = line.split()
                attrs = dict(p.split(":", 1) for p in parts[1:])
                if in_sections:
                    splits.sections.append(
                        SectionDef(parts[0], attrs.get("type", "data"), int(attrs.get("align", "4")))
                    )
                elif current is not None:
                    try:
                        start, end = int(attrs["start"], 16), int(attrs["end"], 16)
                    except KeyError:
                        raise ValueError(f"{where}: expected 'start:0x... end:0x...'")
                    if end <= start:
                        raise ValueError(f"{where}: empty or inverted range")
                    current.ranges.append(SplitRange(parts[0], start, end))
                else:
                    raise ValueError(f"{where}: range outside of a unit")
        splits.validate(str(path))
        return splits

    def validate(self, where: str) -> None:
        seen = set()
        claimed: List[Tuple[int, int, str]] = []
        for unit in self.units:
            if unit.name in seen:
                raise ValueError(f"{where}: unit {unit.name} is listed more than once")
            seen.add(unit.name)
            for r in unit.ranges:
                claimed.append((r.start, r.end, unit.name))
        claimed.sort()
        for (s0, e0, n0), (s1, e1, n1) in zip(claimed, claimed[1:]):
            if s1 < e0:
                raise ValueError(
                    f"{where}: {n0} [0x{s0:08X}, 0x{e0:08X}) overlaps {n1} [0x{s1:08X}, 0x{e1:08X})"
                )

    def unit(self, name: str) -> Optional[Unit]:
        for unit in self.units:
            if unit.name == name:
                return unit
        return None

    def claimed(self, section: str) -> List[Tuple[int, int]]:
        ranges = sorted(
            (r.start, r.end) for u in self.units for r in u.ranges if r.section == section
        )
        return ranges
