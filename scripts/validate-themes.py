#!/usr/bin/env python3
"""
Validate all themes have proper structure with all required colors.
"""

import re
from pathlib import Path


def test_theme_structure(theme_dir):
    """Test that a theme directory has all required variants and colors."""
    day_file = theme_dir / "day.toml"
    night_file = theme_dir / "night.toml"

    errors = []

    # Check both variants exist
    if not day_file.exists():
        errors.append("Missing day.toml")
    if not night_file.exists():
        errors.append("Missing night.toml")

    if errors:
        return False, "; ".join(errors)

    # Check each variant has all colors
    required_bases = [f"base{i:02X}" for i in range(16)]

    for variant_file, variant_name in [(day_file, "day"), (night_file, "night")]:
        content = variant_file.read_text()

        # Check polarity
        if "polarity" not in content:
            errors.append(f"{variant_name}: Missing polarity")

        # Check all base colors
        missing = []
        for base in required_bases:
            if not re.search(rf'{base}\s*=\s*"#[0-9a-fA-F]{{6}}"', content):
                missing.append(base)

        if missing:
            errors.append(f"{variant_name} missing: {', '.join(missing)}")

    if errors:
        return False, "; ".join(errors)

    return True, "Complete structure"


def main():
    """Test all theme directories."""
    # Theme directories are in project root, one level up from scripts/
    project_root = Path(__file__).parent.parent
    
    # Find all theme directories (exclude docs, scripts, assets, .git)
    exclude_dirs = {"docs", "scripts", "assets", ".git"}
    theme_dirs = sorted([
        d for d in project_root.iterdir()
        if d.is_dir() and d.name not in exclude_dirs and not d.name.startswith(".")
    ])

    print("Theme Structure Validation")
    print("=" * 60)
    print(f"Testing {len(theme_dirs)} themes for complete structure...\n")

    passed = 0
    failed = []

    for theme_dir in theme_dirs:
        theme_name = theme_dir.name
        success, message = test_theme_structure(theme_dir)

        status = "OK" if success else "FAIL"
        print(f"[{status}] {theme_name:20s} {message}")

        if success:
            passed += 1
        else:
            failed.append((theme_name, message))

    print("\n" + "=" * 60)
    print(f"Results: {passed}/{len(theme_dirs)} themes have complete structure")

    if failed:
        print(f"\nFailed themes:")
        for name, error in failed:
            print(f"  - {name}: {error}")
        return 1
    else:
        print("\nAll themes have complete structure")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
