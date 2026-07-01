# プロジェクトコンテキスト

> 決定事項のライブドキュメント。設計を決めるたびにここへ追記する。
> 詳細な意思決定の背景・トレードオフは `docs/adr-NNN_*.md`（ADR）に残す。

最終更新: 2026-06-30

## このプロジェクトは何か

Microsoft（Azure AI）Foundry のモデルを使い、**ローカルで動作する軽量・シンプルなコーディングエージェント**を作る。Claude Code のミニ版を、自分の手元で気軽に回せる形で。

「軽量・シンプル」の意味（本人合意）:
- ハーネス（エージェント実装）を小さく保つ
- モデルも軽量系を使う

## 確定した決定

| #   | テーマ              | 決定                                                                 | ADR |
| --- | ------------------- | -------------------------------------------------------------------- | --- |
| D1  | モデルの実行場所    | **(B) Azure AI Foundry（クラウド）**。ローカルで動くのはエージェント本体のみ | -   |
| D2  | 認証                | **`az login`（Entra トークン）で認証。API キーは使わない**           | -   |
| D3  | エージェントの形    | **(A) 対話型 CLI（REPL）** を軸にする。引数ワンショットは後から薄く追加可 | -   |
| D4  | 進め方（フェーズ1） | **Phase 1 は UI/UX のみ**（モデル接続なし）。使い勝手を最優先で固める | -   |
| D5  | UI フレームワーク   | **`rich` + `prompt_toolkit`**（入力=prompt_toolkit / 出力=rich）     | [ADR-001](adr-001_ui-framework.md) |
| D6  | 入力の送信・改行    | **Enter=送信 / 改行=Esc→Enter・Ctrl+J(LF)**。Shift+Enter は端末を「LF送出」設定にすれば Ctrl+J 経由で有効（prompt_toolkit に Shift+Enter キー名が無いため） | -   |
| D7  | 応答プロバイダ      | **インターフェース `respond(messages) -> AsyncIterator[str]` を定義し、Phase 1 はモック実装を挿す**（ストリーミング風表示）。Phase 2 で Foundry 実装に差し替え | -   |
| D8  | ターンの描画        | **ミニマルなチャット形式**（役割は軽い接頭辞/色のみ、枠なし）。**ストリーム中はプレーン → 確定後に Markdown 再レンダリング** | -   |
| D9  | コマンド・操作キー  | `/help` `/clear` `/exit` ＋ **Ctrl+C=応答中断（アプリは生存）/ Ctrl+D=終了 / ↑↓=入力履歴**。`/model` 等モデル絡みは Phase 2 | -   |
| D10 | パッケージ構成・起動 | **`src/agent/` レイアウト**（cli/ui/input/commands/provider に薄く分割）。起動は **`uv run agent`**（`[project.scripts]` で `agent = "agent.cli:main"`） | -   |
| D11 | 入力履歴の永続化    | **`FileHistory` でファイル永続化**。置き場所 `~/.coding-agent/history`（`Path.home()`・依存ゼロ・全OS対応）。パス決定は1関数に閉じる | -   |

## 継承する技術スタック・流儀（`slack-yamada` 由来）

- 言語: **Python 3.13+**、パッケージ管理: **uv**
- LLM 呼び出し: **`openai` SDK** で Foundry の OpenAI 互換エンドポイントを叩く
- 認証: **`azure-identity`**（今回は `az login` トークン → API キー無し）
- コード規約: 型ヒント / `async/await` ベース、ロガーは標準 `logging`、`src/` レイアウト
- 進め方: **フェーズ分けで1つずつ確実に**。各フェーズ完了時に動作確認手順を添える。ハマりどころは先に警告する。勝手に決めずに確認する。

## Phase 2 設計メモ（先取り・実装は未着手）

> Phase 1 完了後に着手する領域の方針を先に固めたもの。確定したら通常の決定テーブルへ昇格する。

### P2-D12: 認証 + SDK の繋ぎ方
- **`azure-identity` のトークンプロバイダ方式**を採用（過去は Bearer 直書きだったが、こちらに寄せる）。
- `get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")` を `AsyncAzureOpenAI(azure_ad_token_provider=...)` に渡す。**API キー不要・トークン自動更新つき**。
- 呼び出しは `model=` に Foundry の**デプロイ名**を渡す。
- **要実機確認（Phase 2 着手時）**: 実リソースのエンドポイント形が Azure OpenAI 形（`*.openai.azure.com` + `api_version` + デプロイ名）か、Foundry Models 形（`*.services.ai.azure.com`）か。後者なら繋ぎ方を調整。

### P2-D13: 資格情報クラス
- **`AzureCliCredential` を採用**（`az login` のログインのみを使用）。ローカル専用なら最速・最も予測可能。
- 資格情報の生成は **`build_credential()` の1関数に閉じる**。将来クラウド化する際は `DefaultAzureCredential` 等への差し替えをここだけで行える。

### P2-D14: モデル選定の方針
- **モデル（デプロイ名）をコンフィグ化**。設定/環境変数 ＋ `/model` コマンドで差し替え可能に。
- **既定は軽量モデル**（暫定 `gpt-5.4-nano`）。Phase 2 着手時に実機のデプロイ一覧を確認して既定を確定する。
- 注意: 軽量すぎるモデルは**多段の tool calling で崩れやすい**。力不足なら `/model` で上位へ逃げる前提。

### P2-D15: エージェントループの構造
- 標準の **tool-use ループ**（送信→tool_calls or 最終回答→ツール実行→結果追記→繰り返し）。
- **最大反復回数のキャップ**（暫定 既定25・コンフィグ可）で暴走/コスト暴発を防ぐ。
- 複数 tool_calls は**逐次実行**（並列は当面避ける）。
- ストリーミングは**段階導入**: Phase 2a=ノンストリームでループ確立 → Phase 2b=`tool_call` delta 蓄積で完全ストリーム化。

### P2-D16: ツール群（フルセットを段階導入）
- 目標は **Claude Code 風フルセット**: `read_file` / `write_file` / `edit` / `run_bash` / `glob` / `grep`。
- **段階導入**: まず4つ（`read_file` / `write_file` / `run_bash` / `edit`）→ 必要に応じ `glob` / `grep` を追加（当面は `run_bash` の `rg`/`grep` で代替可）。
- `edit`（文字列置換）が唯一の難所。**一意一致の保証・空白完全一致・失敗時の良いエラーメッセージ**を丁寧に作る（軽量モデルの自己修復のため）。
- `run_bash` は **timeout / stdout・stderr 捕捉 / 作業ディレクトリ**の取り回しに注意。安全性は P2-D17 で扱う。

### P2-D17: 許可・安全性のモデル
- **階層型・確認つき**。読み取り系（`read_file`/`glob`/`grep`）は**無確認で自動実行**。変更系（`write_file`/`edit`）と `run_bash` は**実行前に確認プロンプト**。
- 確認の選択肢: `y（今回だけ）/ a（セッション中は同種を常に許可）/ n（拒否＋理由をモデルに返す）`。
- 変更系は**差分（diff）を提示してから**確認。
- **作業ディレクトリ境界**: ファイル操作は起動ディレクトリ配下に限定（外は確認 or 拒否）。`run_bash` はシェルゆえ完全には縛れない → 確認ゲートで担保。
- **逃がし弁**: `--yolo` 起動フラグ / `/yolo` で (A)→全自動 に切替可能。

### P2-D18: コンテキスト・履歴管理
- **フル保持＋上限ガード**。履歴はメモリに全保持し、トークン概算で上限接近時に**警告＋古いツール結果から間引き**（or `/clear` 促し）。
- **ツール出力は打ち切り**（先頭/末尾 N 行 or N トークン）。`read_file`/`run_bash` の肥大化を最初から抑える。
- システムプロンプトに**ツールの使い方・作業ディレクトリ・OS** 等を入れる。
- 自動要約（compaction）は**後回し**。長作業で頻繁に上限へ当たると分かってから検討。

### フェーズ・ロードマップ（現時点の見立て）
- **Phase 1**: UI/UX のみ（REPL・モック応答）← **実装済み・実機確認待ち**（ヘッドレス検証＋pytest 16件 通過）。バナーは "AGENT" ブロック文字。UI 文言は英語統一
- **Phase 2a**: Foundry 接続（`az login`/`AzureCliCredential`）＋ツール無しの素の会話、ノンストリーム
- **Phase 2b**: tool-use ループ ＋ コアツール（read/write/run/edit）＋ 許可フロー（diff/確認）＋ ストリーミング化
- **Phase 2c**: `glob`/`grep` 追加、コンテキスト上限ガード／ツール出力打ち切りの作り込み
- **Phase 3+**: OTel 可観測性、ワンショット実行モード、（必要なら）自動要約 compaction

## 後回し（やりたいが今やらない）

- **OTel による可観測性**（トレース/メトリクス）。後のフェーズで導入する。
- 引数によるワンショット実行モード。
- モデル接続・ツール実行（read/write/run 等）── Phase 2 以降。

### D6 補足: Shift+Enter の実装上の制約（Phase 1 実装で判明・重要）

- **prompt_toolkit のキー表には Shift+Enter / Ctrl+Enter という名前が存在しない**（enter エイリアスは `c-m` のみ）。kitty/CSI-u シーケンスも解釈しない。よって `s-enter` バインドは登録不可で、「Shift+Enter を直接バインド」する道は無い。
- 採った方針: 改行は **Esc→Enter（全端末で確実）** と **Ctrl+J（= LF）** をバインド。
  - **Shift+Enter を使いたい場合は、端末側で「Shift+Enter に LF(`\n`) を送る」設定**にする（iTerm2 / VS Code / WezTerm 等で可能）。そうすれば Ctrl+J バインドにそのまま流れて改行になる。
  - これがあるので、手癖の Shift+Enter は「端末設定込み」で実現する、という整理。
- クロスプラットフォーム: `rich`・`prompt_toolkit` とも Windows ネイティブ対応。**Mac / Windows / WSL2 を標準サポート対象**とする。
- 実機確認（未）: 各端末で Esc→Enter / Ctrl+J が改行になること、Shift+Enter→LF 設定が効くこと。

## 検討中・未決

- 使用する具体的なモデル ID（軽量系）── 未決
- 公開するツール群（ファイル読み書き・コマンド実行）の範囲 ── 未決
- 安全性（編集・コマンド実行の確認フロー / 自動実行の可否）── 未決
