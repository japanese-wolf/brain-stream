# BrainStream

> **Note**: This project is currently under development and not yet released. APIs and features may change without notice.

<p align="center">
  <img src="docs/logo.png" alt="BrainStream Logo" width="200">
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

### Two Directions of Discovery

BrainStream accelerates discovery in two complementary directions:

**Direction A: Known -> Unknown** (Breaking filter bubbles)
- You're an expert in Lambda, but did you know WASM runtimes are reshaping serverless?
- Co-occurrence analysis identifies emerging technologies near your stack -- no LLM needed, accuracy grows with data.

**Direction B: Unknown -> Known** (Accelerating understanding)
- A WASM article appears in your feed -- BrainStream explains how it connects to your Lambda experience.
- AI-powered context anchoring ties new information to what you already know.

> A single user can be Direction A in one domain (expert) and Direction B in another (learner). BrainStream serves both.

### Key Features

- **Discovery acceleration**: Trending technologies in your field + personalized tech connections
- **Multi-source aggregation**: AWS, GCP, OpenAI, Anthropic, GitHub Releases, GitHub OSS
- **AI-powered analysis**: Uses your existing Claude Code CLI subscription (on-demand, no background costs)
- **Personalized feed**: Relevance scoring based on your tech stack, domains, roles, and goals
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
┌──────────────────────────────────────────────────────────────┐
│                        BrainStream                           │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │   Plugins    │───>│  Processor   │───>│   Storage    │   │
│  │  (RSS, API)  │    │  (LLM CLI)   │    │  (SQLite)    │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│                              │                    │          │
│                   ┌──────────┴──────────┐         │          │
│                   │  Co-occurrence      │         │          │
│                   │  Analysis (Dir. A)  │         │          │
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
