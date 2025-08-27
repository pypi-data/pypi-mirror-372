# Archer CLI

Archer is a Rich-powered, cancellable TUI/CLI assistant that integrates with the Anthropic API and provides a tool-calling workflow.

## Features
- Beautiful Rich UI with footer and status lines
- Cancellable operations: press ESC while processing
- Tooling: read files, list files, bash, search, and edit files

## Installation
```
pip install archer-cli
```

## Usage
```
archer
```

## Development
- Python >= 3.10
- See `read.py` for the current entrypoint; packaging wraps this via `src/archer_cli/cli.py`.

## License
MIT
