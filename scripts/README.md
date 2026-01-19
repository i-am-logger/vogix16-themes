# Theme Development Scripts

Tools for creating, validating, and managing vogix16 themes.

## Scripts

### `extract-themes.py`

Extracts theme colors from SVG files and generates TOML theme files.

```bash
# Extract all themes from assets/*.svg
python3 scripts/extract-themes.py

# Test extraction on a single theme
python3 scripts/extract-themes.py test
```

**What it does:**
- Parses SVG files from `assets/vogix16_*.svg`
- Extracts base00-base0F colors for both dark and light variants
- Generates TOML theme files in theme directories
- Uses x-coordinate to distinguish dark (left) vs light (right) variants

### `validate-themes.py`

Validates that all theme files have complete structure.

```bash
# Check all themes have base00-base0F in both variants
python3 scripts/validate-themes.py
```

**What it does:**
- Checks each theme has all 16 base colors (base00-base0F)
- Verifies both day and night variants are present
- Reports any missing colors
- Exit code 0 if all valid, 1 if any issues

### `verify-theme-colors.py`

Verifies extracted theme colors match their SVG sources.

```bash
# Compare theme files against SVG sources
python3 scripts/verify-theme-colors.py
```

**What it does:**
- Extracts colors from both SVG and TOML files
- Compares them to ensure extraction was correct
- Reports mismatches
- Useful after modifying extraction script

### `preview-themes.sh`

Quick preview of theme colors in terminal.

```bash
# Display sample colors from all themes
./scripts/preview-themes.sh
```

**What it does:**
- Shows base00 (background), base05 (foreground), base08 (danger) for each theme
- Quick way to verify themes have unique colors
- Useful for spotting extraction issues

## Workflow

When adding new themes or modifying existing ones:

1. **Create/update SVG** in `assets/vogix16_<name>.svg`
2. **Extract**: `python3 scripts/extract-themes.py`
3. **Validate**: `python3 scripts/validate-themes.py`
4. **Verify**: `python3 scripts/verify-theme-colors.py`
5. **Preview**: `./scripts/preview-themes.sh`

## SVG Structure

Scripts expect SVGs with:
- Dark variant on left side (x < 300)
- Light variant on right side (x >= 300)
- Text elements containing `baseXX = "#RRGGBB"` patterns

## Requirements

All scripts require Python 3 with standard library only (no external dependencies).

```bash
# On NixOS
nix-shell -p python3 --run "python3 scripts/extract-themes.py"
```

## Notes

- **base0F**: Often not present in SVGs; scripts preserve existing values
- **TOML Format**: Generated files use consistent formatting
- **Validation**: Always run validate after extraction to catch issues
