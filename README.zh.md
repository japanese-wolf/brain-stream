# BrainStream

> **注意**: 本项目目前正在开发中，尚未正式发布。API和功能可能会在没有通知的情况下发生变化。

<p align="center">
  <img src="docs/icon/icon.svg" alt="BrainStream Logo" width="200">
</p>

<p align="center">
  <strong>发现你不知道自己错过的东西</strong>
</p>

<p align="center">
  <a href="README.md">English</a> |
  <a href="README.ja.md">日本語</a> |
  <a href="README.zh.md">中文</a> |
  <a href="README.ko.md">한국어</a>
</p>

---

## 为什么选择 BrainStream？

你可以向LLM询问任何问题 -- 但前提是你知道该问什么。BrainStream解决了**"未知的未知"问题**：它帮你发现你甚至不知道需要关注的技术和趋势。

### 基于拓扑的偶然发现

BrainStream利用**信息空间拓扑**，无需用户画像或个性化即可自然产生偶然发现：

- **密集集群**代表已充分覆盖的主题 -- 同行工程师们正在阅读的文章
- **集群边界的稀疏区域**揭示领域之间的新兴联系
- **Thompson Sampling**自动平衡新主题探索与已知兴趣利用

> 没有冷启动问题。没有信息茧房。信息的结构本身引导发现。

### 主要功能

- **设计驱动的偶然发现**: 基于拓扑的发现揭示技术领域之间的意外联系
- **多源聚合**: AWS、GCP、OpenAI、Anthropic、GitHub Releases、GitHub OSS
- **AI分析**: 使用你现有的Claude Code CLI订阅（按需使用，无后台成本）
- **一手信息检测**: 区分官方厂商公告和二手报道
- **本地优先**: 数据保存在你自己的机器上
- **插件架构**: 轻松添加新的数据源

## 快速开始

### 安装

```bash
pip install brainstream
```

### 基本命令

```bash
brainstream serve         # 启动 API 服务器
brainstream fetch         # 从所有源获取文章
brainstream status        # 显示文章数、集群和拓扑信息
brainstream sources       # 列出可用数据源
```

## 架构

```
┌──────────────────────────────────────────────────────────────┐
│                        BrainStream                           │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │    插件      │───>│   处理器     │───>│    存储      │   │
│  │  (RSS, API)  │    │  (LLM CLI)   │    │(ChromaDB+SQL)│   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│                              │                    │          │
│                   ┌──────────┴──────────┐         │          │
│                   │  拓扑引擎           │         │          │
│                   │  (HDBSCAN +        │         │          │
│                   │  Thompson Sampling) │         │          │
│                   └─────────────────────┘         │          │
│                                                   ▼          │
│                                           ┌──────────────┐   │
│                                           │    仪表板    │   │
│                                           │  (React)     │   │
│                                           └──────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## 系统要求

- Python 3.11+
- Node.js 18+（用于前端开发）
- Claude Code CLI（可选，用于AI分析）

## 开发

```bash
# 克隆仓库
git clone https://github.com/xxx/brain-stream.git
cd brain-stream

# 后端设置
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 前端设置
cd ../frontend
npm install
npm run dev
```

## Docker

```bash
# 生产环境
docker-compose up -d

# 开发环境（带热重载）
docker-compose -f docker-compose.dev.yml up
```

## 数据源

| 源 | 厂商 | 类型 | 描述 |
|--------|---------|--------|------|
| aws-whatsnew | AWS | RSS | AWS 新功能公告 |
| gcp-release-notes | GCP | RSS | GCP 发布说明 |
| openai-changelog | OpenAI | RSS | OpenAI 博客更新 |
| anthropic-changelog | Anthropic | Scrape | Anthropic 发布说明 |
| github-releases | GitHub | API | GitHub 仓库发布 |

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

## 许可证

本项目采用 GNU Affero 通用公共许可证 v3.0 授权 - 详情请查看 [LICENSE](LICENSE) 文件。
