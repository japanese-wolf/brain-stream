# BrainStream

> **Note**: This project is currently under development and not yet released. APIs and features may change without notice.

<p align="center">
  <img src="docs/icon/icon.svg" alt="BrainStream Logo" width="200">
</p>

<p align="center">
  <strong>Discover What You Didn't Know You Were Missing</strong>
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

## Why BrainStream?

You can ask an LLM anything -- but only if you know what to ask. BrainStream solves the **"unknown unknowns" problem**: it surfaces technologies and trends you didn't even know to look for.

### Topology-Based Serendipity

BrainStream uses **information space topology** to naturally generate serendipity without requiring user profiles or personalization:

- **Dense clusters** represent well-covered topics -- articles your peers are already reading
- **Sparse regions** at cluster boundaries reveal emerging connections between fields
- **Thompson Sampling** automatically balances exploration of new topics vs exploitation of known interests

> No cold-start problem. No filter bubbles. The structure of information itself guides discovery.

### Key Features

- **Serendipity by design**: Topology-based discovery surfaces unexpected connections between technology domains
- **Multi-source aggregation**: AWS, GCP, OpenAI, Anthropic, GitHub Releases, GitHub OSS
- **AI-powered analysis**: Uses your existing Claude Code CLI subscription (on-demand, no background costs)
- **Primary source detection**: Distinguishes official vendor announcements from secondary coverage
- **Local-first**: Your data stays on your machine
- **Plugin architecture**: Easy to add new data sources

## Quick Start

### Installation

```bash
pip install brainstream
```

### Basic Commands

```bash
brainstream serve         # Start the API server
brainstream fetch         # Fetch new articles from all sources
brainstream status        # Show articles, clusters, and topology info
brainstream sources       # List available data sources
```

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        BrainStream                           │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │   Plugins    │───>│  Processor   │───>│   Storage    │   │
│  │  (RSS, API)  │    │  (LLM CLI)   │    │(ChromaDB+SQL)│   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│                              │                    │          │
│                   ┌──────────┴──────────┐         │          │
│                   │  Topology Engine    │         │          │
│                   │  (HDBSCAN +        │         │          │
│                   │  Thompson Sampling) │         │          │
│                   └─────────────────────┘         │          │
│                                                   ▼          │
│                                           ┌──────────────┐   │
│                                           │  Dashboard   │   │
│                                           │  (React)     │   │
│                                           └──────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## Requirements

- Python 3.11+
- Node.js 18+ (for frontend development)
- Claude Code CLI (optional, for AI analysis)

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
- AI processing powered by [Claude Code](https://claude.ai/code)
