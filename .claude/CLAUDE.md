# coding-agent

Microsoft（Azure AI）Foundry のモデルを使う、ローカル動作の軽量・シンプルなコーディングエージェント。

## ドキュメント運用ルール（重要）

- **決定事項は必ず `docs/context.md` に追記する。** 設計を1つ決めるたびに、決定テーブルと該当セクションを更新する。これが最新状態のライブドキュメント。
- **意思決定の背景・選択肢・トレードオフは ADR に残す。** ファイル名は `docs/adr-NNN_<topic>.md`（連番ゼロ埋め、例: `docs/adr-001_ui-framework.md`）。ADR は Status / Date / Context / 選択肢 / Decision / 結果 を含める。
- ADR を追加・更新したら `docs/context.md` の決定テーブルからリンクする。
- 大きめの設計判断は ADR、細かい確定事項は `docs/context.md` のみ、で使い分ける。

## 進め方の流儀

- **フェーズ分けで1つずつ確実に進める。** 各フェーズ完了時に動作確認手順をセットで出す。
- **ハマりどころは先に警告する。**
- **勝手に決めず、迷ったら確認する。**

## 技術スタック・コード規約

- 言語: Python 3.13+ / パッケージ管理: `uv`
- LLM: `openai` SDK で Azure AI Foundry の OpenAI 互換エンドポイントを叩く
- 認証: `azure-identity`。**`az login`（Entra トークン）で認証し、API キーは使わない**
- UI: `rich`（出力）+ `prompt_toolkit`（入力）
- コード: 型ヒント / `async/await` ベース、ロガーは標準 `logging`、`src/` レイアウト
- **UI 文言（ユーザーに表示される文字列）は英語で統一**。バナー・ヘルプ・ツールバー・コマンド応答・エラー・モック応答など。コメント/docstring/docs は当面日本語のまま
- テスト: `pytest`（dev グループ）。`uv run pytest` で実行。async は `tests/conftest.py` の `run()`（`asyncio.run`）でラップし、`pytest-asyncio` は入れない。TTY 必須の実 REPL ループ・実キー入力・見た目はテスト対象外（手動確認）

## 現在のフェーズ

**Phase 1: UI/UX のみ**（モデル接続なし）。REPL の触り心地を固める。
詳細・残課題は `docs/context.md` を参照。
