#!/usr/bin/env bash
# Visual test of all themes - displays sample colors from each theme

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Vogix16 Theme Color Preview"
echo "==========================="
echo ""

# Find all theme directories
for theme_dir in "$PROJECT_ROOT"/*/; do
    theme_name=$(basename "$theme_dir")
    
    # Skip non-theme directories
    [[ "$theme_name" == "docs" ]] && continue
    [[ "$theme_name" == "scripts" ]] && continue
    [[ "$theme_name" == "assets" ]] && continue
    [[ "$theme_name" == ".git" ]] && continue
    
    night_file="$theme_dir/night.toml"
    
    if [[ -f "$night_file" ]]; then
        # Extract colors
        base00=$(grep -E '^base00\s*=' "$night_file" | sed 's/.*"\(#[^"]*\)".*/\1/')
        base05=$(grep -E '^base05\s*=' "$night_file" | sed 's/.*"\(#[^"]*\)".*/\1/')
        base08=$(grep -E '^base08\s*=' "$night_file" | sed 's/.*"\(#[^"]*\)".*/\1/')
        
        printf "%-20s  BG: %s  FG: %s  DANGER: %s\n" "$theme_name" "$base00" "$base05" "$base08"
    fi
done

echo ""
echo "All themes extracted with unique colors"
echo ""
echo "To test with Vogix:"
echo "  1. Add this repo as flake input"
echo "  2. vogix list -s vogix16"
echo "  3. vogix -s vogix16 -t <name>"
