{
  description = "vogix16 color scheme themes for the Vogix theming system";

  outputs =
    { self }:
    {
      # Expose the themes directory
      # Structure: vogix16/{theme}/{variant}.toml
      themes = ./.;
    };
}
