# Contributing to BrainStream

Thank you for your interest in contributing to BrainStream! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate in all interactions. We are committed to providing a welcoming and inclusive environment for everyone.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/brain-stream.git
   cd brain-stream
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Run tests**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   npm test
   ```

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/xxx/brain-stream/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)

### Suggesting Features

1. Check existing [Issues](https://github.com/xxx/brain-stream/issues) for similar suggestions
2. Create a new issue with the `enhancement` label
3. Describe the feature and its use case

### Submitting Pull Requests

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding style guidelines below
   - Add tests for new functionality
   - Update documentation if needed

3. **Commit your changes**
   ```bash
   git commit -m "Add: brief description of changes"
   ```

   Commit message prefixes:
   - `Add:` New feature
   - `Fix:` Bug fix
   - `Update:` Enhancement to existing feature
   - `Refactor:` Code refactoring
   - `Docs:` Documentation changes
   - `Test:` Test additions or changes

4. **Push and create a PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## Coding Style

### Python (Backend)

- Follow [PEP 8](https://pep8.org/)
- Use type hints
- Maximum line length: 100 characters
- Use `ruff` for linting and formatting

```bash
cd backend
ruff check .
ruff format .
```

### TypeScript (Frontend)

- Use TypeScript strict mode
- Follow ESLint configuration
- Use functional components with hooks

```bash
cd frontend
npm run lint
npm run format
```

## Adding a New Data Source Plugin

BrainStream uses a plugin architecture for data sources. To add a new plugin:

1. Create a new file in `backend/src/brainstream/plugins/builtin/`

2. Implement the `BaseSourcePlugin` interface:
   ```python
   from brainstream.plugins.base import BaseSourcePlugin, SourceType, RawArticle

   class MyNewPlugin(BaseSourcePlugin):
       name = "my-new-source"
       vendor = "VendorName"
       source_type = SourceType.RSS  # or API, SCRAPE
       description = "Description of the data source"

       async def fetch_updates(self, since: datetime | None = None) -> list[RawArticle]:
           # Implement fetching logic
           pass
   ```

3. Register the plugin in `registry.py`

4. Add tests in `backend/tests/plugins/`

## Testing

### Backend

```bash
cd backend
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest --cov             # With coverage
pytest tests/plugins/    # Test specific module
```

### Frontend

```bash
cd frontend
npm test                 # Run all tests
npm run test:coverage   # With coverage
```

## Documentation

- Update README if adding new features
- Add docstrings to Python functions
- Comment complex logic

## License

By contributing to BrainStream, you agree that your contributions will be licensed under the AGPL-3.0 License.

## Questions?

Feel free to open an issue for any questions about contributing.
