#!/usr/bin/env python3
"""
Renders the progress of the decompilation as an image.

The picture is a treemap of an objdiff report. Every function is a tile, sized by
the amount of code in it and shaded by how much of it matches. The tiles are grouped
by progress category, which for this project is the library the code belongs to.

The output is SVG, in a light and a dark variant, written without any dependencies.
The tiles themselves are a bitmap embedded in the SVG: there are tens of thousands
of them, which as vector shapes would make a file of several megabytes.

Usage:
    python tools/progress_image.py build/jpn/report.json -o assets/progress.svg \\
        [--dark assets/progress_dark.svg]
"""

import argparse
import base64
import json
import struct
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple
from xml.sax.saxutils import escape

WIDTH = 960
MARGIN = 24
HEADER = 104
MAP_HEIGHT = 440
FOOTER = 36
HEIGHT = HEADER + MAP_HEIGHT + FOOTER
GROUP_GAP = 8  # between categories
GROUP_LABEL = 20  # height of the caption of a category
SCALE = 2  # bitmap pixels per unit of the image, for sharp tiles on dense screens
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"

# Share of matching code -> step of the ramp. The last step is reserved for 100%.
STEPS = [25.0, 50.0, 75.0, 100.0]
STEP_LABELS = ["under 25%", "25–50%", "50–75%", "75–100%", "100%"]


@dataclass
class Theme:
    surface: str
    ink: str
    ink_secondary: str
    ink_muted: str
    empty: str  # functions nothing matches in yet
    ramp: List[str]  # least to most matched


# One hue, light to dark on the light surface and dark to light on the dark one, so
# that "more" always moves away from the surface.
LIGHT = Theme(
    surface="#fcfcfb",
    ink="#0b0b0b",
    ink_secondary="#52514e",
    ink_muted="#898781",
    empty="#e1e0d9",
    ramp=["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"],
)
DARK = Theme(
    surface="#1a1a19",
    ink="#ffffff",
    ink_secondary="#c3c2b7",
    ink_muted="#898781",
    empty="#383835",
    ramp=["#184f95", "#256abf", "#3987e5", "#6da7ec", "#9ec5f4"],
)


@dataclass
class Tile:
    """Anything that takes up area in the map."""

    size: int
    x: float = 0.0
    y: float = 0.0
    w: float = 0.0
    h: float = 0.0


@dataclass
class Function(Tile):
    percent: float = 0.0


@dataclass
class Group(Tile):
    name: str = ""
    functions: List[Function] = field(default_factory=list)

    @property
    def matched(self) -> float:
        return sum(f.size for f in self.functions if f.percent >= 100.0)


def number(value: Any) -> int:
    return int(float(value)) if value is not None else 0


def load_groups(report: Dict[str, Any]) -> List[Group]:
    names = {c["id"]: c.get("name", c["id"]) for c in report.get("categories", [])}
    groups: Dict[str, Group] = {}
    for unit in report.get("units", []):
        categories = unit.get("metadata", {}).get("progress_categories") or ["other"]
        group = groups.get(categories[0])
        if group is None:
            group = groups[categories[0]] = Group(0, name=names.get(categories[0], "Other"))
        for function in unit.get("functions", []):
            size = number(function.get("metadata", {}).get("code_accounting_size", function.get("size")))
            if size:
                group.functions.append(Function(size, percent=float(function.get("fuzzy_match_percent") or 0.0)))
                group.size += size
    return [g for g in groups.values() if g.size]


def worst_ratio(row: Sequence[float], side: float) -> float:
    total = sum(row)
    return max(max(side * side * r / (total * total), total * total / (side * side * r)) for r in row)


def squarify(tiles: Sequence[Tile], x: float, y: float, w: float, h: float) -> None:
    """Lays tiles out in a rectangle, keeping them as close to square as possible."""
    tiles = sorted(tiles, key=lambda t: t.size, reverse=True)
    scale = w * h / sum(t.size for t in tiles)
    areas = [t.size * scale for t in tiles]
    start = 0
    while start < len(tiles):
        side = min(w, h)
        end = start + 1
        row_sum = areas[start]
        # Rows are sorted, so their extremes are the first and the last tile
        best = worst_ratio(areas[start:end], side)
        while end < len(tiles):
            total = row_sum + areas[end]
            ratio = max(
                side * side * areas[start] / (total * total),
                total * total / (side * side * areas[end]),
            )
            if ratio > best:
                break
            best, row_sum, end = ratio, total, end + 1
        thickness = row_sum / side
        offset = 0.0
        for tile, area in zip(tiles[start:end], areas[start:end]):
            length = area / thickness
            if w >= h:
                tile.x, tile.y, tile.w, tile.h = x, y + offset, thickness, length
            else:
                tile.x, tile.y, tile.w, tile.h = x + offset, y, length, thickness
            offset += length
        if w >= h:
            x, w = x + thickness, w - thickness
        else:
            y, h = y + thickness, h - thickness
        start = end


def step_of(percent: float) -> int:
    for i, limit in enumerate(STEPS):
        if percent < limit:
            return i
    return len(STEPS)


def format_percent(value: float) -> str:
    if value >= 10:
        return f"{value:.1f}%"
    if value >= 1:
        return f"{value:.2f}%"
    return f"{value:.3f}%"


def rgb(colour: str) -> Tuple[int, int, int]:
    return int(colour[1:3], 16), int(colour[3:5], 16), int(colour[5:7], 16)


def encode_png(width: int, height: int, pixels: bytearray, palette: List[str]) -> bytes:
    """An 8-bit indexed PNG."""

    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    rows = bytearray()
    for y in range(height):
        rows.append(0)  # filter: none
        rows += pixels[y * width : (y + 1) * width]
    plte = b"".join(bytes(rgb(c)) for c in palette)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 3, 0, 0, 0))
        + chunk(b"PLTE", plte)
        + chunk(b"IDAT", zlib.compress(bytes(rows), 9))
        + chunk(b"IEND", b"")
    )


def draw_tiles(groups: List[Group], theme: Theme) -> bytes:
    """The functions of all groups as a bitmap covering the map area."""
    width, height = (WIDTH - 2 * MARGIN) * SCALE, MAP_HEIGHT * SCALE
    palette = [theme.surface, theme.empty] + theme.ramp
    pixels = bytearray(width * height)  # index 0: the surface
    for group in groups:
        for function in group.functions:
            x0 = round((function.x - MARGIN) * SCALE)
            y0 = round((function.y - HEADER) * SCALE)
            x1 = round((function.x + function.w - MARGIN) * SCALE)
            y1 = round((function.y + function.h - HEADER) * SCALE)
            # A line of surface separates neighbours, unless the tile is too small for one
            if x1 - x0 >= 3:
                x1 -= 1
            if y1 - y0 >= 3:
                y1 -= 1
            x1, y1 = max(x1, x0 + 1), max(y1, y0 + 1)
            index = 1 if function.percent <= 0.0 else 2 + step_of(function.percent)
            run = bytes([index]) * (min(x1, width) - x0)
            for y in range(y0, min(y1, height)):
                pixels[y * width + x0 : y * width + x0 + len(run)] = run
    return encode_png(width, height, pixels, palette)


def render(report: Dict[str, Any], theme: Theme, title: str) -> str:
    measures = report.get("measures", {})
    total_code = number(measures.get("total_code"))
    matched_code = number(measures.get("matched_code"))
    total_functions = number(measures.get("total_functions"))
    matched_functions = number(measures.get("matched_functions"))
    percent = matched_code / total_code * 100 if total_code else 0.0

    # Categories first, then the functions inside each of them, below its caption
    groups = load_groups(report)
    squarify(groups, MARGIN, HEADER, WIDTH - 2 * MARGIN + GROUP_GAP, MAP_HEIGHT + GROUP_GAP)
    for group in groups:
        group.w -= GROUP_GAP
        group.h -= GROUP_GAP
        squarify(group.functions, group.x, group.y + GROUP_LABEL, group.w, group.h - GROUP_LABEL)

    summary = (
        f"{format_percent(percent)} of the code matches: {matched_functions:,} of "
        f"{total_functions:,} functions, {matched_code:,} of {total_code:,} bytes."
    )
    out: List[str] = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        f'aria-labelledby="title desc" font-family="{FONT}">'
    )
    out.append(f'<title id="title">{escape(title)}</title>')
    out.append(f'<desc id="desc">{escape(summary)}</desc>')
    out.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{theme.surface}"/>')

    # Headline
    out.append(
        f'<text x="{MARGIN}" y="58" font-size="44" font-weight="600" fill="{theme.ink}">'
        f"{format_percent(percent)}</text>"
    )
    out.append(
        f'<text x="{MARGIN}" y="84" font-size="14" fill="{theme.ink_secondary}">'
        f"of the code matches · {matched_functions:,} of {total_functions:,} functions · "
        f"{matched_code:,} of {total_code:,} bytes</text>"
    )

    # Legend, right-aligned beside the headline
    entries: List[Tuple[str, str]] = [(theme.empty, "not started")]
    entries += list(zip(theme.ramp, STEP_LABELS))
    widths = [14 + 6 + len(label) * 6.4 + 16 for _, label in entries]
    x = WIDTH - MARGIN - sum(widths) + 16
    out.append(
        f'<text x="{x:.1f}" y="32" font-size="12" fill="{theme.ink_muted}">'
        "Share of a function that matches</text>"
    )
    for (colour, label), width in zip(entries, widths):
        out.append(f'<rect x="{x:.1f}" y="42" width="14" height="14" rx="2" fill="{colour}"/>')
        out.append(
            f'<text x="{x + 20:.1f}" y="53.5" font-size="12" fill="{theme.ink_secondary}">{label}</text>'
        )
        x += width

    # Tiles
    png = base64.b64encode(draw_tiles(groups, theme)).decode("ascii")
    out.append(
        f'<image x="{MARGIN}" y="{HEADER}" width="{WIDTH - 2 * MARGIN}" height="{MAP_HEIGHT}" '
        f'xlink:href="data:image/png;base64,{png}"/>'
    )

    # Captions of the categories
    for group in groups:
        share = group.matched / group.size * 100
        caption = f"{group.name} · {format_percent(share)}"
        if len(caption) * 6.6 > group.w:
            caption = group.name
        if len(caption) * 6.6 > group.w:
            continue
        out.append(
            f'<text x="{group.x:.1f}" y="{group.y + 13:.1f}" font-size="12" font-weight="600" '
            f'fill="{theme.ink_secondary}">{escape(caption)}</text>'
        )

    out.append(
        f'<text x="{MARGIN}" y="{HEADER + MAP_HEIGHT + 24}" font-size="12" fill="{theme.ink_muted}">'
        "Each tile is a function, sized by the amount of code in it. "
        "Which library a function belongs to is an estimate until it has a source file.</text>"
    )
    out.append("</svg>")
    return "\n".join(out) + "\n"


def write_if_changed(path: Path, content: str) -> None:
    if path.is_file() and path.read_text(encoding="utf-8") == content:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    parser.add_argument("report", type=Path, help="objdiff report (report.json)")
    parser.add_argument("-o", "--out", type=Path, required=True, help="output SVG (light)")
    parser.add_argument("--dark", type=Path, help="output SVG for dark backgrounds")
    parser.add_argument("--title", default="Decompilation progress", help="title of the image")
    args = parser.parse_args()

    with open(args.report, "r", encoding="utf-8") as f:
        report = json.load(f)
    write_if_changed(args.out, render(report, LIGHT, args.title))
    if args.dark:
        write_if_changed(args.dark, render(report, DARK, args.title))


if __name__ == "__main__":
    main()
