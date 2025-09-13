# dfixxer-pre-commit

A pre-commit hook for [dfixxer](https://github.com/tuncb/dfixxer), a Delphi/Pascal source code formatter.

## Features

- **Automatic Installation**: Downloads dfixxer binary from GitHub releases if not found
- **Cross-Platform**: Supports Windows, macOS, and Linux (x86_64)
- **Caching**: Downloads binary once and reuses it for better performance
- **Pascal File Support**: Automatically formats `.pas` files before commits

## Usage

Add this to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/tuncb/dfixxer-pre-commit
    rev: main
    hooks:
      - id: dfixxer
```

Then install the git hook scripts:

```bash
pre-commit install
```

## What it does

The hook will:
1. Check if dfixxer is already installed on your system
2. If not found, automatically download the appropriate binary for your platform
3. Cache the binary in `~/.cache/dfixxer-pre-commit/` for future use
4. Run `dfixxer update` on all `.pas` files being committed
5. Format and sort the "uses" sections according to dfixxer's configuration

## Configuration

dfixxer can be configured using a `dfixxer.toml` file in your project root. See the [dfixxer documentation](https://github.com/tuncb/dfixxer) for available options.

## Requirements

- Python 3.6+
- Internet connection (for initial binary download)

## Manual Installation

If you prefer to install dfixxer manually:

```bash
# Install from source (requires Rust)
cargo install --git https://github.com/tuncb/dfixxer

# Or download binary from releases
# https://github.com/tuncb/dfixxer/releases
```