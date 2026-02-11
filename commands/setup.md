---
description: "初回問診 — あなたの技術的関心を登録し、ダイジェストをパーソナライズします"
allowed-tools: [Read, Write, Bash]
---

# BrainStream Setup

ユーザーの技術的関心を収集し、プロファイルとして保存する。
`/brainstream:digest` は本コマンドで生成されたプロファイルを前提として動作する。

## 制約

- 問診は簡潔に。3-4問で完了すること。
- ユーザーの回答をそのまま尊重する。勝手に補完・推測しない。
- 出力は日本語。

## 実行プロトコル

### Step 1: 既存プロファイルの確認

`.claude/brainstream/profile.json` を Read で確認する。

- **ファイルが存在する場合**: 現在のプロファイル内容をユーザーに表示し、「更新しますか？」と確認する。ユーザーが不要と答えた場合は終了。
- **ファイルが存在しない場合**: ディレクトリを作成して問診を開始する。
  ```
  Bash: mkdir -p .claude/brainstream
  ```

### Step 2: 問診

以下の質問を AskUserQuestion で順に行う。

#### Q1: 技術領域（複数選択）

```
質問: どの技術領域に関心がありますか？（複数選択可）
選択肢:
  - Cloud（AWS, GCP, Azure 等）
  - AI・ML（LLM, 機械学習, データサイエンス）
  - DevOps（CI/CD, コンテナ, インフラ自動化）
  - Security（脆弱性, 認証, コンプライアンス）
  - Frontend（React, Vue, Web標準）
  - Backend（API, データベース, マイクロサービス）
  - Mobile（iOS, Android, クロスプラットフォーム）
  - Data（データエンジニアリング, 分析基盤, BI）
multiSelect: true
```

#### Q2: 注目トピック（自由入力歓迎）

Q1 の回答に応じて、関連するトピックの選択肢を動的に構成する。
以下は選択肢の候補一覧。Q1 で選ばれた領域に関連するものを 4 つ選んで提示する。

```
質問: 特に注目しているベンダー・プロジェクト・技術はありますか？（複数選択可、自由入力歓迎）
multiSelect: true
```

**選択肢の候補プール（Q1 の回答に基づき 4 つを選択）:**

| Q1 の領域 | 候補 |
|-----------|------|
| Cloud | AWS, GCP, Azure, Cloudflare |
| AI・ML | OpenAI, Anthropic, Hugging Face, NVIDIA |
| DevOps | GitHub, GitLab, Docker, Kubernetes, Terraform |
| Security | NIST/CVE, GitHub Security, Cloudflare |
| Frontend | React, Next.js, Chrome/Web Standards, Deno |
| Backend | PostgreSQL, Redis, Supabase, NGINX |
| Mobile | Swift/iOS, Kotlin/Android |
| Data | PostgreSQL, MongoDB, Supabase, Grafana |

ユーザーが「Other」で自由入力した場合（例: "Rust", "Zig", "CNCF", "arXiv"）、それをそのまま topics に追加する。
**自由入力を積極的に促すこと。** カタログにないトピックでも WebSearch で探索できる。

#### Q3: 情報の粒度

```
質問: 情報の粒度はどの程度がよいですか？
選択肢:
  - 概要のみ（主要トレンドだけ把握）
  - 重要なものは詳細も（注目度が高い記事は深掘り）
  - すべて詳細（全記事の詳細要約）
multiSelect: false
```

#### Q4: 1日あたりの記事数

```
質問: 1日あたり何件程度の記事が適切ですか？
選択肢:
  - 5件程度（厳選）
  - 10-15件（バランス）
  - 制限なし（全件表示）
multiSelect: false
```

### Step 3: プロファイル生成と保存

問診結果から以下の JSON を生成し、`.claude/brainstream/profile.json` に Write で保存する。

```json
{
  "version": 1,
  "created_at": "ISO-8601 timestamp",
  "updated_at": "ISO-8601 timestamp",
  "interests": {
    "domains": ["cloud", "ai-ml", "devops"],
    "topics": ["AWS", "Anthropic", "Kubernetes"],
    "granularity": "important-detail",
    "max_articles": 15
  }
}
```

**フィールドのマッピング:**

| Q | 回答 | フィールド | 値 |
|---|------|----------|-----|
| Q1 | 選択された領域 | `domains` | 小文字ケバブケース（例: "AI・ML" → "ai-ml"） |
| Q2 | 選択/入力されたトピック | `topics` | そのまま（例: "AWS", "Kubernetes"） |
| Q3 | 概要のみ | `granularity` | `"overview"` |
| Q3 | 重要なものは詳細も | `granularity` | `"important-detail"` |
| Q3 | すべて詳細 | `granularity` | `"full-detail"` |
| Q4 | 5件程度 | `max_articles` | `5` |
| Q4 | 10-15件 | `max_articles` | `15` |
| Q4 | 制限なし | `max_articles` | `0`（0 = 無制限） |

### Step 4: 完了メッセージ

保存後、以下をユーザーに表示:

```
プロファイルを保存しました。

関心領域: [domains をカンマ区切りで表示]
注目トピック: [topics をカンマ区切りで表示]
粒度: [granularity の日本語表示]
記事数目安: [max_articles の日本語表示]

ダイジェストを生成するには `/brainstream:digest` を実行してください。
プロファイルを変更するには `/brainstream:setup` を再実行してください。
```

## 引数

`$ARGUMENTS` が指定された場合:
- `"reset"` — 既存プロファイルを削除して最初からやり直す
- それ以外 — 無視して通常フローを実行
