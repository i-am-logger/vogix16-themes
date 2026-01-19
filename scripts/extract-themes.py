#!/usr/bin/env python3
"""
Extract theme colors from SVG files and generate TOML theme files.
Properly handles dark/light variants side-by-side in SVG.
"""

import re
import sys
from pathlib import Path


def extract_colors_from_svg(svg_path):
    """
    Extract dark and light variant colors from an SVG file.

    SVG structure:
    - Left side (x < 500): Dark theme
    - Right side (x >= 500): Light theme
    """
    content = svg_path.read_text()
    theme_name = svg_path.stem.replace("vogix16_", "")

    # Parse SVG line by line looking for baseXX definitions
    lines = content.split("\n")

    dark_colors = {}
    light_colors = {}

    for i, line in enumerate(lines):
        # Look for text with baseXX = "#RRGGBB"
        # Pattern: base00 = "#262626"
        color_match = re.search(r'(base[0-9A-F]{2})\s*=\s*"(#[0-9a-fA-F]{6})"', line)

        if color_match:
            base_name = color_match.group(1)
            color_value = color_match.group(2).lower()

            # Check x coordinate in the SAME line - dark is left (x < 300), light is right (x >= 300)
            x_match = re.search(r'x="(\d+)"', line)
            if x_match:
                x_pos = int(x_match.group(1))

                if x_pos < 300:
                    # Dark theme (left side)
                    if base_name not in dark_colors:
                        dark_colors[base_name] = color_value
                else:
                    # Light theme (right side)
                    if base_name not in light_colors:
                        light_colors[base_name] = color_value
            else:
                # Fallback: use order - first occurrence = dark, second = light
                if base_name not in dark_colors:
                    dark_colors[base_name] = color_value
                elif base_name not in light_colors:
                    light_colors[base_name] = color_value

    # Validate we have at least base00-base07 for both variants
    required_bases = [f"base{i:02X}" for i in range(8)]

    dark_missing = [b for b in required_bases if b not in dark_colors]
    light_missing = [b for b in required_bases if b not in light_colors]

    if dark_missing:
        print(f"  Warning: Dark variant missing: {', '.join(dark_missing)}", file=sys.stderr)

    if light_missing:
        print(f"  Warning: Light variant missing: {', '.join(light_missing)}", file=sys.stderr)

    if len(dark_colors) < 8 or len(light_colors) < 8:
        print(
            f"  Error: Insufficient colors: dark={len(dark_colors)}, light={len(light_colors)}",
            file=sys.stderr,
        )
        return None

    return {"name": theme_name, "dark": dark_colors, "light": light_colors}


def generate_toml_file(theme_name, variant_name, polarity, colors, output_path):
    """Generate a TOML theme variant file."""
    # Ensure we have all bases, sorted
    all_bases = sorted(colors.keys(), key=lambda x: int(x[4:], 16))

    content = f"""# {theme_name.replace('_', ' ').title()} theme - {variant_name} variant
# Scheme: vogix16

polarity = "{polarity}"

[colors]
"""

    for key in all_bases:
        content += f'{key} = "{colors[key]}"\n'

    output_path.write_text(content)
    return True


def preserve_base0f(theme_dir, dark_colors, light_colors):
    """Preserve existing base0F values if not in SVG."""
    night_file = theme_dir / "night.toml"
    day_file = theme_dir / "day.toml"
    
    if "base0F" not in dark_colors and night_file.exists():
        content = night_file.read_text()
        match = re.search(r'base0F\s*=\s*"(#[0-9a-fA-F]{6})"', content)
        if match:
            dark_colors["base0F"] = match.group(1).lower()
            print(f"    Preserved existing dark base0F: {dark_colors['base0F']}")
    
    if "base0F" not in light_colors and day_file.exists():
        content = day_file.read_text()
        match = re.search(r'base0F\s*=\s*"(#[0-9a-fA-F]{6})"', content)
        if match:
            light_colors["base0F"] = match.group(1).lower()
            print(f"    Preserved existing light base0F: {light_colors['base0F']}")


def test_extraction(svg_path, expected_dark=None, expected_light=None):
    """Test extraction on a single file with optional validation."""
    print(f"\n{'='*60}")
    print(f"Testing: {svg_path.name}")
    print(f"{'='*60}")

    theme_data = extract_colors_from_svg(svg_path)

    if not theme_data:
        print("FAIL: Extraction failed!")
        return False

    print(f"\nOK: Extracted {theme_data['name']}")
    print(f"\nDark variant ({len(theme_data['dark'])} colors):")
    for key in sorted(theme_data["dark"].keys(), key=lambda x: int(x[4:], 16)):
        print(f"  {key} = {theme_data['dark'][key]}")

    print(f"\nLight variant ({len(theme_data['light'])} colors):")
    for key in sorted(theme_data["light"].keys(), key=lambda x: int(x[4:], 16)):
        print(f"  {key} = {theme_data['light'][key]}")

    # Validate if expected values provided
    if expected_dark:
        for key, expected_val in expected_dark.items():
            actual_val = theme_data["dark"].get(key, "MISSING")
            if actual_val.lower() != expected_val.lower():
                print(f"  FAIL: Dark {key}: expected {expected_val}, got {actual_val}")
                return False

    if expected_light:
        for key, expected_val in expected_light.items():
            actual_val = theme_data["light"].get(key, "MISSING")
            if actual_val.lower() != expected_val.lower():
                print(f"  FAIL: Light {key}: expected {expected_val}, got {actual_val}")
                return False

    print("\nOK: All validations passed!")
    return True


def main():
    """Main function to process all SVG files."""
    # Project root is one level up from scripts/
    repo_root = Path(__file__).parent.parent
    assets_dir = repo_root / "assets"
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test mode - validate aikido extraction
        aikido_svg = assets_dir / "vogix16_aikido.svg"

        if not aikido_svg.exists():
            print(f"FAIL: Test file not found: {aikido_svg}")
            return 1

        # Expected values from SVG visual inspection
        expected_dark = {
            "base00": "#262626",  # Sumi (charcoal)
            "base07": "#f6f5f0",  # Washi (paper)
        }
        expected_light = {
            "base00": "#f6f5f0",  # Washi (paper)
            "base07": "#262626",  # Sumi (charcoal)
        }

        success = test_extraction(aikido_svg, expected_dark, expected_light)
        return 0 if success else 1

    # Production mode - extract all themes
    svg_files = sorted(assets_dir.glob("vogix16_*.svg"))

    if not svg_files:
        print("FAIL: No SVG files found in assets/ directory", file=sys.stderr)
        return 1

    print(f"Extracting colors from {len(svg_files)} theme SVG files...")
    print(f"{'='*60}\n")

    successful = 0
    failed = []

    for svg_path in svg_files:
        print(f"Processing {svg_path.name}...")
        theme_data = extract_colors_from_svg(svg_path)

        if theme_data:
            theme_name = theme_data["name"]
            theme_dir = repo_root / theme_name
            
            # Create theme directory if it doesn't exist
            theme_dir.mkdir(exist_ok=True)
            
            # Preserve existing base0F if not in SVG
            preserve_base0f(theme_dir, theme_data["dark"], theme_data["light"])
            
            # Generate night.toml (dark) and day.toml (light)
            night_path = theme_dir / "night.toml"
            day_path = theme_dir / "day.toml"
            
            dark_ok = generate_toml_file(theme_name, "night", "dark", theme_data["dark"], night_path)
            light_ok = generate_toml_file(theme_name, "day", "light", theme_data["light"], day_path)
            
            if dark_ok and light_ok:
                print(f"  OK: {theme_name}/night.toml, {theme_name}/day.toml")
                successful += 1
            else:
                print(f"  FAIL: Failed to write")
                failed.append(svg_path.name)
        else:
            print(f"  FAIL: Extraction failed")
            failed.append(svg_path.name)

    print(f"\n{'='*60}")
    print(f"Results: {successful}/{len(svg_files)} successful")

    if failed:
        print(f"\nFailed themes:")
        for name in failed:
            print(f"  - {name}")
        return 1

    print(f"\nAll themes extracted successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
