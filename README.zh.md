# BrainStream

<p align="center">
  <img src="docs/logo.png" alt="BrainStream Logo" width="200">
</p>

<p align="center">
  <strong>云服务与AI更新的智能中心</strong>
</p>

<p align="center">
  <a href="README.md">English</a> |
  <a href="README.ja.md">日本語</a> |
  <a href="README.zh.md">中文</a> |
  <a href="README.ko.md">한국어</a>
</p>

---

## 什么是 BrainStream？

BrainStream 是一个开源智能中心，帮助工程师被动聚合来自云服务提供商和 AI 厂商的更新信息。它会根据您的技术栈自动收集、摘要和优先排序新闻。

### 主要功能

- **多源聚合**: AWS、GCP、OpenAI、Anthropic、GitHub Releases
- **AI 驱动的摘要**: 使用您现有的 Claude Code 或 Copilot CLI 订阅
- **个性化信息流**: 基于您的技术栈进行相关性评分
- **本地优先**: 数据保存在您自己的机器上
- **插件架构**: 轻松添加新的数据源

## 快速开始

### 安装

```bash
pip install brainstream
```

### 设置

```bash
# 交互式设置向导
brainstream setup

# 启动服务器（自动打开浏览器）
brainstream open
```

### 基本命令

```bash
brainstream open          # 启动服务器并打开仪表板
brainstream fetch         # 手动获取新文章
brainstream status        # 显示收集统计信息
brainstream sources       # 列出可用数据源
```

### 选项

```bash
brainstream open --no-browser      # 不打开浏览器
brainstream open --port 3000       # 指定端口
brainstream open --no-scheduler    # 禁用自动获取
brainstream open --fetch-interval 60  # 设置获取间隔为60分钟
brainstream fetch --skip-llm       # 跳过LLM处理
```

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                       BrainStream                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │    插件      │───▶│   处理器     │───▶│    存储      │  │
│  │  (RSS, API)  │    │  (LLM CLI)   │    │  (SQLite)    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│          │                                       │          │
│          ▼                                       ▼          │
│  ┌──────────────┐                       ┌──────────────┐   │
│  │   调度器     │                       │   仪表板     │   │
│  │  (30分钟)    │                       │  (React)     │   │
│  └──────────────┘                       └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 系统要求

- Python 3.11+
- Node.js 18+（用于前端开发）
- Claude Code CLI 或 GitHub Copilot CLI（可选，用于AI摘要）

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
