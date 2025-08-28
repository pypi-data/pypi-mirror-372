# prettier-markdown

A fast command-line formatter for Markdown files, designed as a replacement for Prettier in Python projects where speed is crucial.

## Installation

```bash
pip install prettier-markdown
```

## Usage

### Command Line

```bash
# Format a single file
prettier-markdown file.md

# Format multiple files
prettier-markdown file1.md file2.md

# Format all markdown files in a directory
prettier-markdown docs/

# Check if files are formatted (exit code 1 if not)
prettier-markdown --check file.md
```

### Pre-commit Hook

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/jsh9/prettier-markdown
    rev: 0.1.0
    hooks:
      - id: prettier-markdown
```
(Replace "0.1.0" with the most recent version.)

## Features

- Fast markdown formatting
- Pre-commit hook integration
- Configurable formatting rules
- Support for multiple markdown files

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run pre-commit hooks
pre-commit run --all-files
```

## License

MIT License
