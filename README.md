# vogix16 Themes

Color themes for the [vogix16 design system](docs/design-system.md), used by [Vogix](https://github.com/i-am-logger/vogix).

<img src="assets/vogix16_example.svg" width="100%" alt="Vogix16 Theme Example">

## Design System

The vogix16 scheme is a semantic design system where colors convey functional meaning:

- **Monochromatic base** (base00-base07): UI structure from background to bright
- **Functional colors** (base08-base0F): Semantic purpose (danger, warning, success, etc.)

See [docs/design-system.md](docs/design-system.md) for the complete philosophy and color usage guidelines.

## Repository Structure

```
vogix16-themes/
├── {theme}/              # Theme directories
│   ├── day.toml          # Light polarity variant
│   └── night.toml        # Dark polarity variant
├── assets/               # Theme preview SVGs
├── docs/
│   └── design-system.md  # vogix16 scheme philosophy
└── scripts/              # Theme development tools
```

## Theme Format

Each variant file contains:

```toml
# Theme name - variant name
# Scheme: vogix16

polarity = "dark"  # or "light"

[colors]
base00 = "#262626"  # Background
base01 = "#333333"  # Surface
base02 = "#3b3028"  # Selection
base03 = "#54433a"  # Comments
base04 = "#6c5d53"  # Borders
base05 = "#a29990"  # Text
base06 = "#cbc3bc"  # Headings
base07 = "#f6f5f0"  # Bright
base08 = "#d7503c"  # Danger
base09 = "#835538"  # Warning
base0A = "#bfa46f"  # Notice
base0B = "#4d5645"  # Success
base0C = "#8694a8"  # Active
base0D = "#658fbd"  # Link
base0E = "#896ea4"  # Highlight
base0F = "#7a5c42"  # Special
```

## Available Themes

19 themes organized into 4 categories:

| Category | Themes |
|----------|--------|
| **Natural** | aikido, arctic_aurora, crystal_cave, desert, forest_night, green, nordic, ocean_depths, sepia, volcanic |
| **Hacker** | cyberspace, ghost, mainframe, matrix |
| **Modern** | blue, futuristic, purple |
| **Vintage** | orange, retro |

**[View Full Theme Gallery with Previews →](THEMES.md)**

## Usage with Vogix

This repository is used as a flake input in Vogix:

```nix
{
  inputs.vogix16-themes.url = "github:i-am-logger/vogix16-themes";
}
```

## Theme Development

### Creating a New Theme

1. Create a new directory with your theme name (lowercase, underscores for spaces)
2. Add `day.toml` (light polarity) and `night.toml` (dark polarity) variants
3. Follow the [design system guidelines](docs/design-system.md)
4. Test with the validation scripts

### Development Scripts

Scripts in `scripts/` help with theme development:

```bash
# Extract colors from SVG mockups
python3 scripts/extract-themes.py

# Validate theme structure
python3 scripts/validate-themes.py

# Verify colors match SVG sources
python3 scripts/verify-theme-colors.py

# Preview theme colors in terminal
./scripts/preview-themes.sh
```

See [scripts/README.md](scripts/README.md) for detailed documentation.

### SVG Assets

The `assets/` directory contains SVG previews of each theme, showing both dark and light variants side-by-side. These are used for:

- Visual reference when designing themes
- Documentation and README display
- Color extraction via `extract-themes.py`

## Contributing

1. Fork this repository
2. Create your theme following the format above
3. Run validation scripts to ensure correctness
4. Submit a pull request with:
   - Theme files (`{name}/day.toml`, `{name}/night.toml`)
   - SVG preview (`assets/vogix16_{name}.svg`) - optional but appreciated
   - Brief description of the theme's inspiration

### Theme Guidelines

- **Monochromatic base**: base00-base07 should form a cohesive progression
- **Functional colors**: base08-base0F maintain semantic meaning per the design system
- **Contrast**: Ensure sufficient contrast for accessibility
- **Both variants**: Include both day (light) and night (dark) variants

## License

[CC BY-NC-SA 4.0](LICENSE) - Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
