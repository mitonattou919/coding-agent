"""スラッシュコマンド（D9: /help /clear /exit）。"""

from __future__ import annotations

from .provider import Message
from .ui import UI

# handle() の戻り値:
#   "exit"    -> ループを抜けて終了
#   "handled" -> コマンドを処理した（通常入力には進まない）


def is_command(text: str) -> bool:
    return text.startswith("/")


def handle(text: str, ui: UI, messages: list[Message]) -> str:
    cmd = text.split()[0].lower()

    if cmd in ("/exit", "/quit"):
        return "exit"

    if cmd == "/clear":
        messages.clear()
        ui.console.clear()
        ui.note("Conversation cleared.")
        return "handled"

    if cmd == "/help":
        ui.show_help()
        return "handled"

    ui.error(f"Unknown command: {cmd}")
    ui.note("Type /help to see available commands.")
    return "handled"
