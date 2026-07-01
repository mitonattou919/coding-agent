"""ターミナル出力（D5: rich / D8: ミニマルなチャット表示）。

ストリーム中はプレーンテキストで逐次表示し、確定後に Markdown として
再レンダリングする。スピナー・中断表示もここで扱う。
"""

from __future__ import annotations

import asyncio
from typing import AsyncIterator

from rich.console import Console
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.text import Text

from . import __version__

USER_STYLE = "bold cyan"
AGENT_STYLE = "bold green"
DIM = "dim"

# "AGENT" のブロック文字ロゴ（バナー用）
WORDMARK = "▄▀█ █▀▀ █▀▀ █▄░█ ▀█▀\n█▀█ █▄█ ██▄ █░▀█ ░█░"


class UI:
    def __init__(self) -> None:
        self.console = Console()

    def banner(self) -> None:
        self.console.print()
        self.console.print(Text(WORDMARK, style="bold cyan"))
        self.console.print()
        self.console.print(
            Text("coding-agent", style="bold")
            + Text(f" · v{__version__} · Phase 1 (UI only)", style=DIM)
        )
        self.console.print(
            Text("/help", style="cyan") + Text(" for commands", style=DIM)
        )
        self.console.print()

    def note(self, message: str) -> None:
        self.console.print(Text(message, style=DIM))

    def error(self, message: str) -> None:
        self.console.print(Text(message, style="bold red"))

    def show_help(self) -> None:
        self.console.print(
            Markdown(
                "**Commands**\n\n"
                "- `/help` — show this help\n"
                "- `/clear` — clear conversation history and screen\n"
                "- `/exit` (`/quit`) — quit\n\n"
                "**Keys**\n\n"
                "- `Enter` — send\n"
                "- `Esc→Enter` / `Ctrl+J` — newline "
                "(Shift+Enter works if your terminal sends LF)\n"
                "- `Ctrl+C` — interrupt the current response (the app keeps running); "
                "cancels the line while typing\n"
                "- `Ctrl+D` — quit\n"
                "- `↑` / `↓` — input history\n"
            )
        )

    async def stream_response(self, stream: AsyncIterator[str]) -> str:
        """応答をストリーミング表示し、確定後に Markdown 再描画する。

        ストリーム中は `Live(transient=True)` でプレーン表示し、終了時に消去 →
        最終テキストを Markdown としてもう一度描く（D8）。
        Ctrl+C 由来のキャンセル時は、ここまでの部分テキストを描いて返す。
        """
        from rich.live import Live

        text = ""
        interrupted = False
        try:
            with Live(
                Spinner("dots", text=Text(" Thinking…", style=DIM)),
                console=self.console,
                transient=True,
                refresh_per_second=20,
            ) as live:
                async for chunk in stream:
                    text += chunk
                    live.update(Text(text))
        except asyncio.CancelledError:
            interrupted = True

        if text:
            self.console.print(Markdown(text))
        else:
            self.console.print(Text("(no response)", style=DIM))
        if interrupted:
            self.console.print(Text("(interrupted)", style=DIM))
        self.console.print()
        return text
