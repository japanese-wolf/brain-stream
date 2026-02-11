# BrainStream

> **注意**: このプロジェクトは現在開発中であり、まだ公開されていません。APIや機能は予告なく変更される可能性があります。

<p align="center">
  <img src="docs/icon/icon.svg" alt="BrainStream Logo" width="200">
</p>

<p align="center">
  <strong>「知らなかったこと」を発見する</strong>
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

## なぜ BrainStream？

LLMには何でも聞ける -- でも「何を聞くべきか」を知っている必要があります。BrainStreamは**「知らないことを知らない」問題**を解決します。あなたが探そうともしなかった技術やトレンドを届けます。

BrainStreamは**Claude Codeプラグイン**として動作する、パーソナルな技術情報エージェントです。複数のソースから記事を収集し、構造化された要約を生成し、トピック別にクラスタリングし、階層的なダイジェストを提供します — すべて開発ワークフローの中で。

### 主な機能

- **エージェントベースの収集**: LLMエージェントが設定されたソースから自律的に記事を取得・処理
- **構造化された要約**: 各記事をWhat / Who / Why it mattersの形式で要約
- **階層的ダイジェスト**: 全体概要 → クラスタ別トレンド → 個別記事
- **一次情報の検出**: ベンダー公式発表 (🏷️) と二次的なカバレッジ (📝) を区別
- **マルチソース集約**: AWS、GCP、OpenAI、Anthropic、GitHub
- **ローカルファースト**: データはプロジェクトの `.claude/brainstream/` ディレクトリに保存
- **外部依存なし**: Claude Codeの組み込みツール (WebFetch, Read, Write) を使用

## クイックスタート

### インストール

```bash
# Claude Codeプラグインとしてインストール
claude plugin add github:japanese-wolf/brain-stream

# または開発用にローカルで読み込み
claude --plugin-dir /path/to/brain-stream
```

### 使い方

```bash
# 今日のテックダイジェストを生成
/brainstream:digest

# 特定のベンダーのみ取得
/brainstream:digest AWS

# 今日のキャッシュデータを使用
/brainstream:digest cached
```

### 出力例

```markdown
# Tech Digest — 2026-02-11

## 概要
6つのソースから24件の記事を収集し、5つのクラスタに分類しました。
注目: AIモデルのデプロイコストが低下傾向、GitHub Actionsにセキュリティの大型アップデート。

## AI Infrastructure
> 複数のベンダーがモデルサービングのコスト最適化機能をリリース。

### Amazon Bedrock の Claude モデル価格引き下げ 🏷️
**What**: AWSがAnthropicモデルのBedrock料金を30%引き下げ。
**Who**: AWS
**Why it matters**: 本番LLMデプロイメントの障壁が低下。
🔗 https://aws.amazon.com/...
```

## アーキテクチャ

```
┌──────────────────────────────────────────────────────┐
│                  BrainStream Plugin                    │
├──────────────────────────────────────────────────────┤
│                                                       │
│  /brainstream:digest                                  │
│       │                                               │
│       ├── WebFetch ──> RSS/HTML ソース                 │
│       │                                               │
│       ├── LLM ──> 要約 (What/Who/Why)                 │
│       │                                               │
│       ├── LLM ──> トピック別クラスタリング               │
│       │                                               │
│       └── Write ──> .claude/brainstream/              │
│                     ├── cache/YYYY-MM-DD.json         │
│                     └── digests/YYYY-MM-DD.md         │
└──────────────────────────────────────────────────────┘
```

## データソース

| ソース | ベンダー | タイプ | 説明 |
|--------|---------|--------|------|
| aws-whatsnew | AWS | RSS | AWS の新着情報 |
| gcp-release-notes | GCP | RSS | GCP リリースノート |
| openai-blog | OpenAI | RSS | OpenAI ブログ更新 |
| anthropic-news | Anthropic | Scrape | Anthropic リリースノート |
| github-blog | GitHub | RSS | GitHub Blog |
| github-changelog | GitHub | RSS | GitHub Changelog |

## データ保存先

ランタイムデータはプロジェクトの `.claude/brainstream/` ディレクトリに保存されます:

```
.claude/brainstream/
├── cache/
│   └── 2026-02-11.json    # 記事の生データ (JSON)
└── digests/
    └── 2026-02-11.md      # 生成済みダイジェスト (Markdown)
```

## 必要要件

- [Claude Code](https://claude.ai/code) 1.0.33以上

## コントリビューション

コントリビューションを歓迎します！ガイドラインは [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

## ライセンス

このプロジェクトは GNU Affero General Public License v3.0 の下でライセンスされています。詳細は [LICENSE](LICENSE) ファイルをご覧ください。
