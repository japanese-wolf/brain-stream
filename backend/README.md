# BrainStream Backend

Intelligence hub for engineers to passively aggregate cloud and AI vendor updates.

## Installation

```bash
pip install brainstream
```

## Quick Start

```bash
# Initial setup
brainstream setup

# Start the dashboard
brainstream open
```

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .
```

## CLI Commands

- `brainstream open` - Start server and open dashboard
- `brainstream setup` - Interactive setup wizard
- `brainstream fetch` - Fetch updates from all sources
- `brainstream status` - Show collection status
- `brainstream config` - View/modify configuration
