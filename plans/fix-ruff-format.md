# Ruff format CI エラー修正計画

## 背景

PR #5 の Ruff ワークフローで `ruff format --check --diff` が失敗している。
56ファイルにフォーマット差分があり、これは今回のPRで導入した変更ではなく既存コードベース全体の問題。

## 失敗の原因

`ruff format` が未適用のファイルが56件存在する（src/, tests/, examples/ にまたがる）。
`ruff check`（lint）は通過しているが、`ruff format`（コードフォーマット）が未実施。

## 実施計画

### ステップ1: ruff format を全体に適用

```bash
uv run ruff format
```

56ファイルが自動フォーマットされる。

### ステップ2: フォーマット結果の確認

```bash
uv run ruff format --check
uv run ruff check
uv run pytest
```

フォーマット適用後に lint とテストが壊れていないことを確認する。

### ステップ3: コミットしてプッシュ

フォーマット修正を develop ブランチにコミット・プッシュし、PR #5 の CI を再実行させる。

## 変更対象

`uv run ruff format` により自動修正される56ファイル（src/, tests/, examples/ にまたがる）。
