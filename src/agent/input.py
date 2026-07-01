"""入力まわり（D6 キーバインド / D11 履歴永続化）。

- Enter = 送信 / 改行 = Esc→Enter・Ctrl+J（= LF）
- ↑↓ で入力履歴を遡る。履歴は ~/.coding-agent/history に永続化。

Shift+Enter について（docs/context.md D6 参照）:
prompt_toolkit のキー表には Shift+Enter / Ctrl+Enter という名前自体が無く、
kitty/CSI-u シーケンスも解釈しない。そのため「s-enter」は登録できない。
現実的な経路は「端末側で Shift+Enter に LF(\\n) を送らせる」設定で、
これは下の Ctrl+J バインドにそのまま流れる（iTerm2 / VS Code / WezTerm 等で設定可）。
どの端末でも確実なのは Esc→Enter。
"""

from __future__ import annotations

from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings


def history_path() -> Path:
    """入力履歴ファイルのパス。決定ロジックはこの1関数に閉じる（D11）。"""
    base = Path.home() / ".coding-agent"
    base.mkdir(parents=True, exist_ok=True)
    return base / "history"


def _build_keybindings() -> KeyBindings:
    kb = KeyBindings()

    @kb.add("enter")
    def _submit(event) -> None:
        event.current_buffer.validate_and_handle()

    def _newline(event) -> None:
        event.current_buffer.insert_text("\n")

    # 改行: Esc→Enter（全端末で確実） と Ctrl+J（= LF）。
    # 端末が Shift+Enter に LF を送る設定なら、その Shift+Enter もここに流れる。
    kb.add("escape", "enter")(_newline)
    kb.add("c-j")(_newline)

    return kb


def _bottom_toolbar() -> HTML:
    return HTML(
        " <b>Enter</b> send   "
        "<b>Esc→Enter / Ctrl+J</b> newline   "
        "<b>Ctrl+C</b> interrupt   "
        "<b>Ctrl+D</b> quit   "
        "<b>/help</b> "
    )


def build_session() -> PromptSession:
    return PromptSession(
        multiline=True,
        key_bindings=_build_keybindings(),
        history=FileHistory(str(history_path())),
        bottom_toolbar=_bottom_toolbar,
    )


def prompt_fragments() -> HTML:
    return HTML("<ansicyan><b>› </b></ansicyan>")
