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

---

## なぜ BrainStream？

LLMには何でも聞ける -- でも「何を聞くべきか」を知っている必要があります。BrainStreamは**「知らないことを知らない」問題**を解決します。あなたが探そうともしなかった技術やトレンドを届けます。

### トポロジーベースのセレンディピティ

BrainStreamは**情報空間のトポロジー**を活用し、ユーザープロファイルやパーソナライズなしにセレンディピティを自然に生み出します：

- **密なクラスタ**はよくカバーされたトピック -- 他のエンジニアも読んでいる記事
- **クラスタ境界の疎な領域**が分野間の新しいつながりを明らかにする
- **Thompson Sampling**が新しいトピックの探索と既知の興味の活用を自動調整

> コールドスタート問題なし。フィルタバブルなし。情報の構造そのものが発見を導きます。

### 主な機能

- **設計によるセレンディピティ**: トポロジーベースの発見が技術ドメイン間の予想外のつながりを浮かび上がらせる
- **マルチソース集約**: AWS、GCP、OpenAI、Anthropic、GitHub Releases、GitHub OSS
- **AI分析**: 既存のClaude Code CLIサブスクリプションを活用（オンデマンド、バックグラウンドコスト不要）
- **一次情報の検出**: ベンダー公式発表と二次的なカバレッジを区別
- **ローカルファースト**: データは自分のマシンに保存
- **プラグインアーキテクチャ**: 新しいデータソースを簡単に追加可能

## クイックスタート

### インストール

```bash
pip install brainstream
```

### 基本コマンド

```bash
brainstream serve         # APIサーバーを起動
brainstream fetch         # 全ソースから記事を取得
brainstream status        # 記事数、クラスタ、トポロジー情報を表示
brainstream sources       # 利用可能なデータソース一覧
```

## アーキテクチャ

```
┌──────────────────────────────────────────────────────────────┐
│                        BrainStream                           │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │  プラグイン   │───>│  プロセッサ   │───>│  ストレージ   │   │
│  │  (RSS, API)  │    │  (LLM CLI)   │    │(ChromaDB+SQL)│   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│                              │                    │          │
│                   ┌──────────┴──────────┐         │          │
│                   │ トポロジーエンジン   │         │          │
│                   │ (HDBSCAN +          │         │          │
│                   │  Thompson Sampling) │         │          │
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
