# BrainStream

<p align="center">
  <img src="docs/logo.png" alt="BrainStream Logo" width="200">
</p>

<p align="center">
  <strong>Intelligence Hub for Cloud & AI Updates</strong>
</p>

<p align="center">
  <a href="README.md">English</a> |
  <a href="README.ja.md">日本語</a> |
  <a href="README.zh.md">中文</a> |
  <a href="README.ko.md">한국어</a>
</p>

<p align="center">
  <a href="https://github.com/xxx/brain-stream/actions"><img src="https://github.com/xxx/brain-stream/workflows/CI/badge.svg" alt="CI"></a>
  <a href="https://github.com/xxx/brain-stream/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-AGPL%20v3-blue.svg" alt="License"></a>
  <a href="https://pypi.org/project/brainstream/"><img src="https://img.shields.io/pypi/v/brainstream" alt="PyPI"></a>
</p>

---

## What is BrainStream?

BrainStream is an open-source intelligence hub that helps engineers passively aggregate updates from cloud providers and AI vendors. It automatically collects, summarizes, and prioritizes news based on your tech stack.

### Key Features

- **Multi-source aggregation**: AWS, GCP, OpenAI, Anthropic, GitHub Releases
- **AI-powered summaries**: Uses your existing Claude Code or Copilot CLI subscription
- **Personalized feed**: Relevance scoring based on your tech stack
- **Local-first**: Your data stays on your machine
- **Plugin architecture**: Easy to add new data sources

## Quick Start

### Installation

```bash
pip install brainstream
```

### Setup

```bash
# Interactive setup wizard
brainstream setup

# Start the server (opens browser automatically)
brainstream open
```

### Basic Commands

```bash
brainstream open          # Start server and open dashboard
brainstream fetch         # Manually fetch new articles
brainstream status        # Show collection statistics
brainstream sources       # List available data sources
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       BrainStream                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Plugins     │───▶│  Processor   │───▶│   Storage    │  │
│  │  (RSS, API)  │    │  (LLM CLI)   │    │  (SQLite)    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│          │                                       │          │
│          ▼                                       ▼          │
│  ┌──────────────┐                       ┌──────────────┐   │
│  │  Scheduler   │                       │  Dashboard   │   │
│  │  (30 min)    │                       │  (React)     │   │
│  └──────────────┘                       └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Requirements

- Python 3.11+
- Node.js 18+ (for frontend development)
- Claude Code CLI or GitHub Copilot CLI (optional, for AI summaries)

## Development

```bash
# Clone repository
git clone https://github.com/xxx/brain-stream.git
cd brain-stream

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Frontend setup
cd ../frontend
npm install
npm run dev
```

## Docker

```bash
# Production
docker-compose up -d

# Development (with hot reload)
docker-compose -f docker-compose.dev.yml up
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/), [React](https://react.dev/), and [Tailwind CSS](https://tailwindcss.com/)
- AI processing powered by [Claude Code](https://claude.ai/code) and [GitHub Copilot](https://github.com/features/copilot)
