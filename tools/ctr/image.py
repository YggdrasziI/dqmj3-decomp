"""
Version configuration (config/<version>/config.toml) and access to the code image.

A 3DS `code.bin` is a flat dump of three page-aligned segments (text, rodata, data)
that are mapped contiguously starting at the address of the text segment. The zero
initialized `.bss` follows the data segment in memory and has no bytes in the file.
"""

import hashlib
import struct
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

PAGE_SIZE = 0x1000


@dataclass
class Section:
    name: str
    kind: str  # "code", "rodata", "data" or "bss"
    address: int
    size: int

    @property
    def end(self) -> int:
        return self.address + self.size

    def contains(self, addr: int) -> bool:
        return self.address <= addr < self.end


@dataclass
class StringPoolDef:
    """Where armlink put the merged contents of a string section. See strpool.py."""

    section: str  # name of the section in compiled objects, e.g. ".conststring"
    address: int
    size: int
    char_size: int = 1

    @property
    def end(self) -> int:
        return self.address + self.size


@dataclass
class InitArrayDef:
    """Where armlink put the static initializer table (the .init_array sections).

    Each entry is the offset from the entry to an initializer function (+1 for
    Thumb), not its address. See notes/BUILD_SYSTEM.md."""

    address: int
    size: int

    @property
    def end(self) -> int:
        return self.address + self.size


@dataclass
class RegionDef:
    """An address range of .text attributed to a library. See config.toml."""

    id: str
    name: str
    start: int
    end: int


class VersionConfig:
    def __init__(self, path: Path) -> None:
        self.path = path
        with open(path, "rb") as f:
            data = tomllib.load(f)
        self.name: str = data["name"]
        self.version: str = data["version"]
        self.object = Path(data["object"])
        self.hash: str = data["hash"].lower()
        self.symbols_path = Path(data["symbols"])
        self.splits_path = Path(data["splits"])
        self.sections: List[Section] = [
            Section(s["name"], s["type"], s["address"], s["size"])
            for s in data["sections"]
        ]
        self.sections.sort(key=lambda s: s.address)
        self.string_pools: List[StringPoolDef] = [
            StringPoolDef(p["section"], p["address"], p["size"], p.get("char_size", 1))
            for p in data.get("string_pools", [])
        ]
        # Functions armlink inlined into every caller and then removed: name -> the
        # one instruction of their body (before `bx lr`)
        self.inlined_functions: Dict[str, int] = {}
        for f in data.get("inlined_functions", []):
            instruction = f["instruction"]
            if not isinstance(instruction, int) or not 0 <= instruction <= 0xFFFFFFFF:
                raise ValueError(f"{path}: instruction of {f['symbol']} is not a 32-bit word")
            self.inlined_functions[f["symbol"]] = instruction
        init_array = data.get("init_array")
        self.init_array: Optional[InitArrayDef] = (
            InitArrayDef(init_array["address"], init_array["size"]) if init_array else None
        )
        self.regions: List[RegionDef] = sorted(
            (RegionDef(r["id"], r["name"], r["start"], r["end"]) for r in data.get("regions", [])),
            key=lambda r: r.start,
        )
        self.base = self.sections[0].address
        self.sections_by_name: Dict[str, Section] = {s.name: s for s in self.sections}

    def section(self, name: str) -> Section:
        return self.sections_by_name[name]

    def string_pool_at(self, addr: int) -> Optional[StringPoolDef]:
        for pool in self.string_pools:
            if pool.address <= addr < pool.end:
                return pool
        return None

    def region_at(self, addr: int) -> Optional[RegionDef]:
        for region in self.regions:
            if region.start <= addr < region.end:
                return region
        return None

    def section_at(self, addr: int) -> Optional[Section]:
        for section in self.sections:
            if section.contains(addr):
                return section
        return None

    @property
    def file_size(self) -> int:
        """Size of code.bin: every loaded segment is padded to a page boundary."""
        end = max(s.end for s in self.sections if s.kind != "bss")
        return ((end - self.base) + PAGE_SIZE - 1) & ~(PAGE_SIZE - 1)

    @property
    def memory_end(self) -> int:
        return max(s.end for s in self.sections)


class Image:
    """The original (or rebuilt) code image, addressed by virtual address."""

    def __init__(self, config: VersionConfig, data: bytes) -> None:
        self.config = config
        self.data = data
        self.base = config.base

    @staticmethod
    def load(config: VersionConfig, path: Optional[Path] = None, verify: bool = True) -> "Image":
        path = path or config.object
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            raise SystemExit(
                f"error: {path} not found.\n"
                f"Place the decompressed code.bin of your game dump there (see README.md)."
            )
        if verify:
            digest = hashlib.sha1(data).hexdigest()
            if digest != config.hash:
                hint = ""
                if len(data) < config.file_size:
                    hint = (
                        "\nThe file is smaller than expected: it is probably still compressed."
                        " Extract it with `ctrtool --decompresscode`."
                    )
                raise SystemExit(
                    f"error: {path} does not match the expected SHA-1.\n"
                    f"  expected: {config.hash}\n"
                    f"  actual:   {digest}{hint}"
                )
        return Image(config, data)

    def offset(self, addr: int) -> int:
        return addr - self.base

    def has_bytes(self, addr: int, size: int = 1) -> bool:
        return self.base <= addr and addr + size <= self.base + len(self.data)

    def read(self, addr: int, size: int) -> bytes:
        off = addr - self.base
        return self.data[off : off + size]

    def u32(self, addr: int) -> int:
        return struct.unpack_from("<I", self.data, addr - self.base)[0]

    def u16(self, addr: int) -> int:
        return struct.unpack_from("<H", self.data, addr - self.base)[0]

    def u8(self, addr: int) -> int:
        return self.data[addr - self.base]
