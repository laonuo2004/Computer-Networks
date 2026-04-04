from __future__ import annotations

import argparse
from pathlib import Path

BIT_WIDTH = 56
HALF_WIDTH = BIT_WIDTH / 2
LEFT = 120
TOP = 64
ROW_GAP = 92
AMP = 22


def sanitize_bits(raw: str) -> str:
    bits = "".join(raw.split())
    if not bits or any(ch not in "01" for ch in bits):
        raise ValueError("bits must contain only 0 and 1")
    return bits


def nrz(bits: str) -> list[int]:
    return [1 if bit == "1" else 0 for bit in bits]


def nrzi(bits: str) -> list[int]:
    level = 0
    levels: list[int] = []
    for bit in bits:
        if bit == "1":
            level = 1 - level
        levels.append(level)
    return levels


def manchester(bits: str) -> list[int]:
    levels: list[int] = []
    for bit in bits:
        levels.extend((1, 0) if bit == "0" else (0, 1))
    return levels


def differential_manchester(bits: str) -> list[int]:
    level = 0
    levels: list[int] = []
    for bit in bits:
        if bit == "0":
            level = 1 - level
        levels.append(level)
        level = 1 - level
        levels.append(level)
    return levels


def clock(bits: str) -> list[int]:
    levels: list[int] = []
    for _ in bits:
        levels.extend((1, 0))
    return levels


def y_for_level(base_y: float, level: int) -> float:
    return base_y - AMP if level == 1 else base_y + AMP


def step_path(levels: list[int], step: float, base_y: float) -> str:
    x = LEFT
    path = [f"M {x} {y_for_level(base_y, levels[0])}"]
    for i, level in enumerate(levels):
        x += step
        path.append(f"H {x}")
        if i + 1 < len(levels) and levels[i + 1] != level:
            path.append(f"V {y_for_level(base_y, levels[i + 1])}")
    return " ".join(path)


def text(x: float, y: float, content: str, size: int = 18, weight: int = 400, anchor: str = "start") -> str:
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
        f'text-anchor="{anchor}" fill="#1f2937">{content}</text>'
    )


def line(x1: float, y1: float, x2: float, y2: float, dash: str | None = None, width: float = 1.2) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="#c9c2b8" stroke-width="{width}"{dash_attr} />'
    )


def path(d: str) -> str:
    return (
        f'<path d="{d}" fill="none" stroke="#111827" stroke-width="3" '
        'stroke-linejoin="round" stroke-linecap="round" />'
    )


def build_svg(bits: str) -> str:
    width = LEFT + len(bits) * BIT_WIDTH + 28
    height = TOP + ROW_GAP * 5

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
    ]

    for i in range(len(bits) + 1):
        x = LEFT + i * BIT_WIDTH
        parts.append(line(x, TOP - 30, x, height - 28, dash="4 5", width=1))

    for i, bit in enumerate(bits):
        x = LEFT + i * BIT_WIDTH + BIT_WIDTH / 2
        parts.append(text(x, TOP - 38, bit, size=20, weight=700, anchor="middle"))

    rows = [
        ("NRZ", nrz(bits), BIT_WIDTH),
        ("NRZI", nrzi(bits), BIT_WIDTH),
        ("Manchester", manchester(bits), HALF_WIDTH),
        ("Diff Manchester", differential_manchester(bits), HALF_WIDTH),
        ("Clock", clock(bits), HALF_WIDTH),
    ]

    for index, (name, levels, step) in enumerate(rows):
        base_y = TOP + index * ROW_GAP
        parts.append(text(18, base_y + 8, name, size=18, weight=700))
        parts.append(line(LEFT - 14, base_y, width - 18, base_y))
        parts.append(path(step_path(levels, step, base_y)))

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render line encoding waveforms as SVG.")
    parser.add_argument("bits", nargs="?", default="1001111100010001")
    parser.add_argument(
        "-o",
        "--output",
        default="line_encoding.svg",
        help="output SVG path",
    )
    args = parser.parse_args()

    bits = sanitize_bits(args.bits)
    svg = build_svg(bits)
    output_path = Path(args.output)
    output_path.write_text(svg, encoding="utf-8")
    print(f"wrote {output_path.resolve()}")


if __name__ == "__main__":
    main()
