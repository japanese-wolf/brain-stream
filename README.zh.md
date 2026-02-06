# BrainStream

> **注意**: 本项目目前正在开发中，尚未正式发布。API和功能可能会在没有通知的情况下发生变化。

<p align="center">
  <img src="docs/logo.png" alt="BrainStream Logo" width="200">
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

### 双向发现

BrainStream从两个互补方向加速发现：

**方向A：已知 → 未知**（打破信息茧房）
- 你是Lambda专家，但你知道WASM运行时正在重塑无服务器架构吗？
- 共现分析识别你技术栈附近的新兴技术 -- 无需LLM，数据越多越准确。

**方向B：未知 → 已知**（加速理解）
- 当WASM文章出现在你的信息流中时，BrainStream会解释它与你的Lambda经验有何关联。
- AI驱动的上下文锚定将新信息与你已知的知识联系起来。

> 同一个用户可以在一个领域处于方向A（专家），在另一个领域处于方向B（学习者）。BrainStream同时服务于两者。

### 主要功能

- **发现加速**: 你所在领域的趋势技术 + 个性化技术连接
- **多源聚合**: AWS、GCP、OpenAI、Anthropic、GitHub Releases、GitHub OSS
- **AI分析**: 使用你现有的Claude Code CLI订阅（按需使用，无后台成本）
- **个性化信息流**: 基于技术栈、领域、角色和目标的相关性评分
- **本地优先**: 数据保存在你自己的机器上
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

## 架构

```
┌──────────────────────────────────────────────────────────────┐
│                        BrainStream                           │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │    插件      │───>│   处理器     │───>│    存储      │   │
│  │  (RSS, API)  │    │  (LLM CLI)   │    │  (SQLite)    │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│                              │                    │          │
│                   ┌──────────┴──────────┐         │          │
│                   │  共现分析           │         │          │
│                   │  (方向A)            │         │          │
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
