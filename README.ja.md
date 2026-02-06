# BrainStream

> **注意**: このプロジェクトは現在開発中であり、まだ公開されていません。APIや機能は予告なく変更される可能性があります。

<p align="center">
  <img src="docs/logo.png" alt="BrainStream Logo" width="200">
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

---

## なぜ BrainStream？

LLMには何でも聞ける -- でも「何を聞くべきか」を知っている必要があります。BrainStreamは**「知らないことを知らない」問題**を解決します。あなたが探そうともしなかった技術やトレンドを届けます。

### 二方向の発見

BrainStreamは2つの方向で発見を加速します:

**方向A: 既知 → 未知**（フィルタバブルを破る）
- Lambdaの専門家でも、WASMランタイムがサーバーレスを変えつつあることは知らないかもしれません
- 共起分析があなたのスタック周辺の新興技術を特定 -- LLM不要、データが増えるほど精度向上

**方向B: 未知 → 既知**（理解を加速する）
- WASMの記事がフィードに現れたとき、あなたのLambda経験とどう関連するかを説明します
- AIによる文脈アンカリングが、新しい情報を既知の知識に結びつけます

> 一人のユーザーが、あるドメインでは方向A（専門家）、別のドメインでは方向B（学習者）になり得ます。BrainStreamは両方に対応します。

### 主な機能

- **発見の加速**: あなたの分野のトレンド技術 + パーソナライズされた技術接続
- **マルチソース集約**: AWS、GCP、OpenAI、Anthropic、GitHub Releases、GitHub OSS
- **AI分析**: 既存のClaude Code CLIサブスクリプションを活用（オンデマンド、バックグラウンドコスト不要）
- **パーソナライズドフィード**: テックスタック、分野、役割、目標に基づく関連性スコアリング
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

## アーキテクチャ

```
┌──────────────────────────────────────────────────────────────┐
│                        BrainStream                           │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │  プラグイン   │───>│  プロセッサ   │───>│  ストレージ   │   │
│  │  (RSS, API)  │    │  (LLM CLI)   │    │  (SQLite)    │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│                              │                    │          │
│                   ┌──────────┴──────────┐         │          │
│                   │  共起分析           │         │          │
│                   │  (方向A)            │         │          │
│                   └─────────────────────┘         │          │
│                                                   ▼          │
│                                           ┌──────────────┐   │
│                                           │ ダッシュボード │   │
│                                           │  (React)     │   │
│                                           └──────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## 必要要件

- Python 3.11以上
- Node.js 18以上（フロントエンド開発用）
- Claude Code CLI（AI分析用、オプション）

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
