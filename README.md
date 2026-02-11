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
  <a href="https://github.com/japanese-wolf/brain-stream/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-AGPL%20v3-blue.svg" alt="License"></a>
</p>

---

## Why BrainStream?

You can ask an LLM anything -- but only if you know what to ask. BrainStream solves the **"unknown unknowns" problem**: it surfaces technologies and trends you didn't even know to look for.

BrainStream is a **Claude Code plugin** that acts as your personal tech intelligence agent. It collects articles from multiple sources, generates structured summaries, clusters them by topic, and delivers a hierarchical digest — all within your development workflow.

### Key Features

- **Agent-based collection**: LLM agent autonomously fetches and processes articles from configured sources
- **Structured summaries**: Each article summarized as What / Who / Why it matters
- **Hierarchical digest**: Overview → Cluster trends → Individual articles
- **Primary source detection**: Distinguishes official vendor announcements (🏷️) from secondary coverage (📝)
- **Multi-source aggregation**: AWS, GCP, OpenAI, Anthropic, GitHub
- **Local-first**: Data stays in your project's `.claude/brainstream/` directory
- **No external dependencies**: Uses Claude Code's built-in tools (WebFetch, Read, Write)

## Quick Start

### Installation

```bash
# Install as a Claude Code plugin
claude plugin add github:japanese-wolf/brain-stream

# Or load locally for development
claude --plugin-dir /path/to/brain-stream
```

### Usage

```bash
# Generate today's tech digest
/brainstream:digest

# Fetch only from a specific vendor
/brainstream:digest AWS

# Use cached data from today
/brainstream:digest cached
```

### Output Example

```markdown
# Tech Digest — 2026-02-11

## Overview
Collected 24 articles from 6 sources, organized into 5 clusters.
Key trends: AI model deployment costs dropping; GitHub Actions gets major security update.

## AI Infrastructure
> Multiple vendors releasing cost-optimization features for model serving.

### Amazon Bedrock price reduction for Claude models 🏷️
**What**: AWS reduced Bedrock pricing for Anthropic models by 30%.
**Who**: AWS
**Why it matters**: Lowers the barrier for production LLM deployments.
🔗 https://aws.amazon.com/...
```

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                  BrainStream Plugin                    │
├──────────────────────────────────────────────────────┤
│                                                       │
│  /brainstream:digest                                  │
│       │                                               │
│       ├── WebFetch ──> RSS/HTML Sources               │
│       │                                               │
│       ├── LLM ──> Summarize (What/Who/Why)            │
│       │                                               │
│       ├── LLM ──> Cluster by Topic                    │
│       │                                               │
│       └── Write ──> .claude/brainstream/              │
│                     ├── cache/YYYY-MM-DD.json         │
│                     └── digests/YYYY-MM-DD.md         │
└──────────────────────────────────────────────────────┘
```

## Data Sources

| Source | Vendor | Type | Description |
|--------|--------|------|-------------|
| aws-whatsnew | AWS | RSS | AWS What's New announcements |
| gcp-release-notes | GCP | RSS | GCP release notes |
| openai-blog | OpenAI | RSS | OpenAI blog updates |
| anthropic-news | Anthropic | Scrape | Anthropic release notes |
| github-blog | GitHub | RSS | GitHub Blog |
| github-changelog | GitHub | RSS | GitHub Changelog |

## Data Storage

Runtime data is stored in the project's `.claude/brainstream/` directory:

```
.claude/brainstream/
├── cache/
│   └── 2026-02-11.json    # Raw article data (JSON)
└── digests/
    └── 2026-02-11.md      # Generated digest (Markdown)
```

## Requirements

- [Claude Code](https://claude.ai/code) 1.0.33+

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
