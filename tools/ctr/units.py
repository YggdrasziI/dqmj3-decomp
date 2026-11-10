"""
Resolves the list of translation units of a version.

Units come from two places:

  - splits.txt assigns address ranges to source files
  - everything no source file claims yet is grouped into automatically generated
    units so that the whole image is accounted for when measuring progress

Automatic units are laid out on a fixed address grid. Their names therefore do not
change as ranges get claimed, they only shrink (and eventually disappear).

The merged string pools are not part of any unit. Their contents show up in the
objects of the units that refer to them instead (see split.py).
"""

from typing import Dict, List, Optional, Tuple

from .image import Section, VersionConfig
from .symbols import SplitRange, Splits, SymbolTable, Unit

AUTO_PREFIX = "auto/"
AUTO_GRID = 0x10000


def subtract(start: int, end: int, claimed: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Parts of [start, end) not covered by the sorted ranges in `claimed`."""
    free = []
    cur = start
    for c_start, c_end in claimed:
        if c_end <= cur:
            continue
        if c_start >= end:
            break
        if c_start > cur:
            free.append((cur, c_start))
        cur = max(cur, c_end)
    if cur < end:
        free.append((cur, end))
    return free


def auto_unit_name(section: Section, addr: int, category: Optional[str]) -> str:
    cell = addr - (addr - section.address) % AUTO_GRID
    group = f"{category}/" if category else ""
    return f"{AUTO_PREFIX}{group}{section.name.lstrip('.')}_{cell:08X}"


def resolve_units(config: VersionConfig, splits: Splits, symbols: SymbolTable) -> List[Unit]:
    units: List[Unit] = list(splits.units)
    auto: Dict[str, Unit] = {}

    for section in config.sections:
        claimed = splits.claimed(section.name)
        for c_start, c_end in claimed:
            if not (section.address <= c_start and c_end <= section.end):
                raise ValueError(
                    f"{config.splits_path}: range [0x{c_start:08X}, 0x{c_end:08X}) is not inside {section.name}"
                )
            for pool in config.string_pools:
                if c_start < pool.end and pool.address < c_end:
                    raise ValueError(
                        f"{config.splits_path}: range [0x{c_start:08X}, 0x{c_end:08X}) overlaps the "
                        f"{pool.section} string pool, which does not belong to any one unit"
                    )
        # Merged string pools are shared by every unit that refers to a string in them
        pools = [(p.address, p.end) for p in config.string_pools if section.contains(p.address)]
        claimed = sorted(claimed + pools)
        for free_start, free_end in subtract(section.address, section.end, claimed):
            # Cut the free space at grid lines and where one library ends and the next
            # begins, but never through the middle of a symbol
            lines = set()
            line = free_start - (free_start - section.address) % AUTO_GRID + AUTO_GRID
            while line < free_end:
                lines.add(line)
                line += AUTO_GRID
            for region in config.regions:
                lines.update(a for a in (region.start, region.end) if free_start < a < free_end)
            cuts = [free_start]
            for line in sorted(lines):
                sym = symbols.containing(line)
                cut = line
                if sym is not None and sym.address < line < sym.end:
                    cut = min(sym.end, free_end)
                if cuts[-1] < cut < free_end:
                    cuts.append(cut)
            cuts.append(free_end)
            for start, end in zip(cuts, cuts[1:]):
                region = config.region_at(start)
                category = region.id if region is not None else None
                name = auto_unit_name(section, start, category)
                unit = auto.get(name)
                if unit is None:
                    unit = Unit(name, auto=True, category=category)
                    auto[name] = unit
                unit.ranges.append(SplitRange(section.name, start, end))

    units.extend(sorted(auto.values(), key=lambda u: u.ranges[0].start))
    return units


def object_name(unit: Unit) -> str:
    """Path of the unit's object file relative to an object directory."""
    name = unit.name
    for ext in (".cpp", ".c", ".s"):
        if name.endswith(ext):
            name = name[: -len(ext)]
            break
    return name + ".o"
