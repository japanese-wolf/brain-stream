---
description: "パーソナライズ設定の表示・変更"
allowed-tools: [Read, Write, Bash]
---

# BrainStream Config

パーソナライズ設定の表示・変更を行う。

## 実行プロトコル

### Step 1: 設定ファイルの読み込み

`.claude/brainstream/config.json` を Read で読み込む。

**ファイルが存在しない場合**: デフォルト設定で初期化する。

```json
{
  "version": 1,
  "history_tracking": false,
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601"
}
```

### Step 2: 現在の設定表示

現在の設定をユーザーに表示する:

```
## BrainStream 設定

| 設定項目 | 現在の値 | 説明 |
|---------|----------|------|
| 行動履歴の記録 | ON / OFF | 深掘りした記事やクラスタを記録し、今後のダイジェストに反映 |

プロファイル: .claude/brainstream/profile.json
設定: .claude/brainstream/config.json
```

行動履歴が ON の場合、蓄積された履歴の統計も表示する:
- 記録数
- 最もよく深掘りしたトピック上位3件

### Step 3: 変更内容の確認

AskUserQuestion で変更したい項目を確認する。

```
質問: 何を変更しますか？
選択肢:
  - 行動履歴の記録を ON にする / OFF にする（現在の状態に応じて逆を表示）
  - プロファイルを再設定する（/brainstream:setup を実行）
  - 行動履歴をクリアする
  - 変更なし（終了）
multiSelect: false
```

### Step 4: 設定変更の実行

#### 行動履歴の ON/OFF 切替

`config.json` の `history_tracking` を更新し、Write で保存する。

- **ON にした場合**: 「行動履歴の記録を有効にしました。深掘りした記事やクラスタが記録され、ダイジェストのパーソナライズに活用されます。」
- **OFF にした場合**: 「行動履歴の記録を無効にしました。既存の履歴データは保持されます（削除する場合は「行動履歴をクリア」を選択してください）。」

#### プロファイル再設定

「`/brainstream:setup` を実行してください。」と案内して終了。

#### 行動履歴のクリア

確認を取ってから `.claude/brainstream/history/actions.json` を削除する:

```
Bash: rm -f .claude/brainstream/history/actions.json
```

「行動履歴をクリアしました。」と表示。

## 引数

`$ARGUMENTS` の解釈:

- **指定なし** — 設定の表示・変更フローを実行
- **"show"** — 現在の設定のみ表示（変更しない）
- **"history on"** — 行動履歴を ON にして終了
- **"history off"** — 行動履歴を OFF にして終了
- **"clear-history"** — 行動履歴をクリアして終了
