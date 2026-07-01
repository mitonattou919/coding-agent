# coding-agent

Microsoft（Azure AI）Foundry のモデルを使う、**ローカルで動く軽量・シンプルなコーディングエージェント**。

> 開発はフェーズ分けで進行中。**現在 Phase 1（UI/UX のみ・モデル未接続）**。
> 設計の決定事項は [`docs/context.md`](docs/context.md)、背景は [`docs/`](docs/) の ADR を参照。

## 必要なもの

- Python 3.13（`uv` が自動取得）
- [uv](https://docs.astral.sh/uv/)

## セットアップ & 起動

```bash
uv sync
uv run agent
```

## 使い方（Phase 1）

対話型 REPL です。指示を入力すると、モック応答がストリーミング表示されます（モデルは Phase 2 で接続）。

| 操作 | キー |
| --- | --- |
| 送信 | `Enter` |
| 改行 | `Esc→Enter` / `Ctrl+J` |
| 応答の中断（アプリは終了しない） | `Ctrl+C` |
| 終了 | `Ctrl+D` |
| 入力履歴 | `↑` / `↓` |

コマンド: `/help` `/clear` `/exit`

> **Shift+Enter で改行したい場合**: prompt_toolkit には Shift+Enter キー名が無いため、
> 端末側で「Shift+Enter に LF（`\n`）を送る」設定にしてください（iTerm2 / VS Code / WezTerm 等）。
> 設定すると `Ctrl+J` バインド経由で改行になります。`Esc→Enter` はどの端末でも確実に動きます。

## 構成

```
src/agent/
├── cli.py        # エントリポイント（REPL ループ）
├── ui.py         # rich 描画（バナー / ストリーム / Markdown 確定）
├── input.py      # prompt_toolkit（キーバインド / 履歴）
├── commands.py   # スラッシュコマンド
└── provider.py   # respond() インターフェース + モック実装
```
