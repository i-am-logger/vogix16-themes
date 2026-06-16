#!/usr/bin/env python3
"""Generate the SVG theme previews FROM the TOMLs (the source of truth).

The TOML is canonical; this renders assets/vogix16_<theme>.svg from
<theme>/{night,day}.toml so the preview can never drift from what ships.
Poetic monochromatic swatch names (Sumi, Washi, …) are preserved from the
existing SVG where present; functional slots use the canonical vogix16 role
names. Run with --check to fail if any committed SVG is out of date.

  python3 scripts/generate-previews.py           # (re)write all SVGs
  python3 scripts/generate-previews.py --check    # CI: verify up-to-date
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ASSETS = ROOT / "assets"
SKIP = {"docs", "scripts", "assets"}

MONO = ["Background", "Surface", "Overlay", "Comment", "Border", "Foreground", "Heading", "Bright"]
ROLE = ["Success", "Warning", "Notice", "Danger", "Active", "Link", "Highlight", "Special"]
KEYS = [f"base{i:02X}" for i in range(16)]
W, ROW, TOP = 500, 30, 100


def read_toml(p):
    d = {}
    for line in p.read_text().splitlines():
        m = re.match(r'\s*(base[0-9A-Fa-f]{2})\s*=\s*"(#[0-9a-fA-F]{6})"', line)
        if m:
            d["base" + m.group(1)[4:].upper()] = m.group(2).lower()
    return d


def lum(h):
    def c(x):
        x = int(x, 16) / 255
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4

    return 0.2126 * c(h[1:3]) + 0.7152 * c(h[3:5]) + 0.0722 * c(h[5:7])


def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def read_existing_mono_names(svg):
    """{(col, baseNN): name} for base00-07 from an existing SVG ('dark'/'light')."""
    names, titles = {}, {}
    if not svg.exists():
        return names, titles
    for line in svg.read_text().splitlines():
        m = re.search(r'x="(\d+)"[^>]*>(base0[0-7]) = "#[0-9a-fA-F]{6}" # ([^<]+?)\s*</text>', line)
        if m:
            col = "dark" if int(m.group(1)) < 300 else "light"
            names[(col, m.group(2))] = m.group(3).strip()
        t = re.search(r'font-weight="bold"[^>]*>(.*?) (Dark|Light)</text>', line)
        if t:
            titles[t.group(2).lower()] = t.group(1)
    return names, titles


def label_fill(color, bg, fg):
    return color if contrast(color, bg) >= 3.0 else fg


def column(x0, colors, title, theme, mono_names):
    bg, fg = colors["base00"], colors["base05"]
    out = [
        f'  <text x="{x0 + 250}" y="40" font-family="sans-serif" font-size="20" '
        f'font-weight="bold" text-anchor="middle" fill="{colors["base07"]}">{title}</text>'
    ]
    out.append(
        f'  <text x="{x0 + 60}" y="80" font-family="monospace" font-size="14" '
        f'fill="{fg}"># {theme.replace("_", " ").title()} monochromatic scale</text>'
    )
    rx, tx = x0 + 60, x0 + 90
    for i, key in enumerate(KEYS):
        if i == 8:
            out.append(
                f'  <text x="{rx}" y="{TOP + 8 * ROW + 20}" font-family="monospace" '
                f'font-size="14" fill="{fg}"># Functional colors</text>'
            )
        y = TOP + i * ROW + (50 if i >= 8 else 0)
        col = colors.get(key)
        if not col:
            continue
        name = mono_names.get(key) if i < 8 else ROLE[i - 8]
        if not name:
            name = MONO[i]
        stroke = ' stroke="' + fg + '" stroke-width="1"' if i == 0 else ""
        out.append(f'  <rect x="{rx}" y="{y}" width="20" height="20" rx="2" fill="{col}"{stroke}/>')
        out.append(
            f'  <text x="{tx}" y="{y + 15}" font-family="monospace" font-size="14" '
            f'fill="{label_fill(col, bg, fg)}">{key} = "{col}" # {name}</text>'
        )
    return "\n".join(out)


def render(theme, dark, light, names, titles):
    H = TOP + 16 * ROW + 70
    dt = titles.get("dark", f"{theme.replace('_', ' ').title()}") + " Dark"
    lt = titles.get("light", f"{theme.replace('_', ' ').title()}") + " Light"
    dn = {k: names.get(("dark", k)) for k in KEYS}
    ln = {k: names.get(("light", k)) for k in KEYS}
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{H}" viewBox="0 0 1000 {H}">\n'
        f"  <!-- {theme.replace('_', ' ').title()} theme — generated from {theme}/{{night,day}}.toml by "
        f"scripts/generate-previews.py; edit the TOML, not this file. -->\n"
        f'  <rect x="0" y="0" width="{W}" height="{H}" fill="{dark["base00"]}"/>\n'
        f'  <rect x="{W}" y="0" width="{W}" height="{H}" fill="{light["base00"]}"/>\n'
        + column(0, dark, dt, theme, dn)
        + "\n"
        + column(W, light, lt, theme, ln)
        + "\n</svg>\n"
    )


def main():
    check = "--check" in sys.argv
    themes = sorted(
        d.name for d in ROOT.iterdir() if d.is_dir() and d.name not in SKIP and not d.name.startswith(".")
    )
    stale = []
    for t in themes:
        nf, df = ROOT / t / "night.toml", ROOT / t / "day.toml"
        if not (nf.exists() and df.exists()):
            continue
        names, titles = read_existing_mono_names(ASSETS / f"vogix16_{t}.svg")
        svg = render(t, read_toml(nf), read_toml(df), names, titles)
        path = ASSETS / f"vogix16_{t}.svg"
        cur = path.read_text() if path.exists() else None
        if check:
            if cur != svg:
                stale.append(t)
        else:
            path.write_text(svg)
            print(f"{'updated' if cur != svg else 'ok     '} assets/vogix16_{t}.svg")
    if check:
        if stale:
            print("Out-of-date previews (run scripts/generate-previews.py): " + ", ".join(stale))
            return 1
        print("All previews are up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
