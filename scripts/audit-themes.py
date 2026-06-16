#!/usr/bin/env python3
"""Audit every theme for the objective vogix16 quality bars.

Fails (exit 1) if any variant violates:
  - base00-07 is a STRICTLY MONOTONE luminance ramp (dark asc / light desc)
  - base05 (main text) on base00 (bg) meets WCAG AA >= 4.5:1
  - each functional color base08-0F meets >= 4.5:1 on base00

Hue choice (success=green vs red, etc.) is editorial/cultural and NOT checked.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKIP = {"docs", "scripts", "assets"}


def parse(p):
    d = {}
    for line in p.read_text().splitlines():
        m = re.match(r'\s*(base[0-9A-Fa-f]{2})\s*=\s*"(#[0-9a-fA-F]{6})"', line)
        if m:
            d["base" + m.group(1)[4:].upper()] = m.group(2)
    return d


def _lin(x):
    x = int(x, 16) / 255
    return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4


def lum(h):
    h = h.lstrip("#")
    return 0.2126 * _lin(h[0:2]) + 0.7152 * _lin(h[2:4]) + 0.0722 * _lin(h[4:6])


def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def audit(name, colors):
    issues = []
    ramp = [colors.get(f"base{i:02d}") for i in range(8)]
    if not all(ramp):
        issues.append("ramp missing base00-07")
    else:
        ls = [lum(c) for c in ramp]
        asc = all(ls[i] < ls[i + 1] for i in range(7))
        desc = all(ls[i] > ls[i + 1] for i in range(7))
        if not (asc or desc):
            bad = [
                f"base0{i}->base0{i + 1}"
                for i in range(7)
                if not (ls[i] < ls[i + 1]) and not (ls[i] > ls[i + 1])
            ]
            issues.append(f"ramp non-monotone ({', '.join(bad)})")
    bg, fg = colors.get("base00"), colors.get("base05")
    if bg and fg:
        cr = contrast(bg, fg)
        if cr < 4.5:
            issues.append(f"text contrast base05/base00 = {cr:.2f}:1 (< 4.5)")
    for c in "89ABCDEF":
        fn = colors.get(f"base0{c}")
        if bg and fn:
            cr = contrast(bg, fn)
            if cr < 4.5:
                issues.append(f"base0{c} on base00 = {cr:.2f}:1 (< 4.5)")
    return issues


def main():
    themes = sorted(
        d.name for d in ROOT.iterdir() if d.is_dir() and d.name not in SKIP and not d.name.startswith(".")
    )
    failed = 0
    for t in themes:
        for variant in ("night", "day"):
            p = ROOT / t / f"{variant}.toml"
            if not p.exists():
                continue
            issues = audit(f"{t}/{variant}", parse(p))
            if issues:
                failed += 1
                print(f"[FAIL] {t}/{variant}: " + "; ".join(issues))
            else:
                print(f"[OK]   {t}/{variant}")
    print("=" * 60)
    if failed:
        print(f"{failed} variant(s) failed the ramp/contrast bars.")
        return 1
    print("All themes pass: monotone ramps + WCAG AA contrast.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
