# BrainStream

<p align="center">
  <img src="docs/logo.png" alt="BrainStream Logo" width="200">
</p>

<p align="center">
  <strong>クラウド・AI アップデートのためのインテリジェンスハブ</strong>
</p>

<p align="center">
  <a href="README.md">English</a> |
  <a href="README.ja.md">日本語</a> |
  <a href="README.zh.md">中文</a> |
  <a href="README.ko.md">한국어</a>
</p>

---

## BrainStream とは？

BrainStream は、エンジニアがクラウドプロバイダーや AI ベンダーからの更新情報を受動的に集約できるオープンソースのインテリジェンスハブです。あなたの技術スタックに基づいて、ニュースを自動的に収集、要約、優先順位付けします。

### 主な機能

- **マルチソース集約**: AWS、GCP、OpenAI、Anthropic、GitHub Releases
- **AI による要約**: 既存の Claude Code または Copilot CLI サブスクリプションを活用
- **パーソナライズドフィード**: 技術スタックに基づく関連性スコアリング
- **ローカルファースト**: データは自分のマシンに保存
- **プラグインアーキテクチャ**: 新しいデータソースを簡単に追加可能

## クイックスタート

### インストール

```bash
pip install brainstream
```

### セットアップ

```bash
# 対話形式のセットアップウィザード
brainstream setup

# サーバー起動（ブラウザが自動で開きます）
brainstream open
```

### 基本コマンド

```bash
brainstream open          # サーバー起動 & ダッシュボードを開く
brainstream fetch         # 手動で記事を取得
brainstream status        # 収集統計を表示
brainstream sources       # 利用可能なデータソース一覧
```

### オプション

```bash
brainstream open --no-browser      # ブラウザを開かない
brainstream open --port 3000       # ポート指定
brainstream open --no-scheduler    # 自動取得を無効化
brainstream open --fetch-interval 60  # 取得間隔を60分に設定
brainstream fetch --skip-llm       # LLM処理をスキップ
```

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                       BrainStream                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  プラグイン   │───▶│  プロセッサ   │───▶│  ストレージ   │  │
│  │  (RSS, API)  │    │  (LLM CLI)   │    │  (SQLite)    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│          │                                       │          │
│          ▼                                       ▼          │
│  ┌──────────────┐                       ┌──────────────┐   │
│  │ スケジューラー │                       │ ダッシュボード │   │
│  │  (30分間隔)   │                       │  (React)     │   │
│  └──────────────┘                       └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 必要要件

- Python 3.11以上
- Node.js 18以上（フロントエンド開発用）
- Claude Code CLI または GitHub Copilot CLI（AI要約用、オプション）

## 開発

```bash
# リポジトリをクローン
git clone https://github.com/xxx/brain-stream.git
cd brain-stream

# バックエンドセットアップ
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# フロントエンドセットアップ
cd ../frontend
npm install
npm run dev
```

## Docker

```bash
# 本番環境
docker-compose up -d

# 開発環境（ホットリロード付き）
docker-compose -f docker-compose.dev.yml up
```

## データソース

| ソース | ベンダー | タイプ | 説明 |
|--------|---------|--------|------|
| aws-whatsnew | AWS | RSS | AWS の新着情報 |
| gcp-release-notes | GCP | RSS | GCP リリースノート |
| openai-changelog | OpenAI | RSS | OpenAI ブログ更新 |
| anthropic-changelog | Anthropic | Scrape | Anthropic リリースノート |
| github-releases | GitHub | API | GitHub リポジトリのリリース |

## コントリビューション

コントリビューションを歓迎します！ガイドラインは [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

## ライセンス

このプロジェクトは GNU Affero General Public License v3.0 の下でライセンスされています。詳細は [LICENSE](LICENSE) ファイルをご覧ください。
