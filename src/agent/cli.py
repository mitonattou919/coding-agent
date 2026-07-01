"""エントリポイント（D3: 対話型 REPL / D10: `uv run agent`）。

asyncio で REPL ループを回す。Phase 1 は応答にモックプロバイダを使う。
"""

from __future__ import annotations

import asyncio

from . import commands
from .input import build_session, prompt_fragments
from .provider import Message, MockProvider, ResponseProvider
from .ui import UI


async def _respond(ui: UI, provider: ResponseProvider, messages: list[Message]) -> str | None:
    """応答をストリーミングしつつ、Ctrl+C で「その応答だけ」中断する（D9）。

    ストリーム表示タスクを別タスクで回し、KeyboardInterrupt が来たら
    タスクをキャンセルする。stream_response 側は CancelledError を
    受け取って部分テキストを描画し、テキストを返す。
    """
    task = asyncio.ensure_future(ui.stream_response(provider.respond(messages)))
    try:
        return await task
    except KeyboardInterrupt:
        task.cancel()
        try:
            return await task
        except asyncio.CancelledError:
            return None


async def run() -> None:
    ui = UI()
    provider: ResponseProvider = MockProvider()
    session = build_session()
    messages: list[Message] = []

    ui.banner()

    while True:
        try:
            line = await session.prompt_async(prompt_fragments())
        except KeyboardInterrupt:
            # 入力中の Ctrl+C は行を取り消して継続
            continue
        except EOFError:
            # Ctrl+D で終了
            break

        line = line.strip()
        if not line:
            continue

        if commands.is_command(line):
            if commands.handle(line, ui, messages) == "exit":
                break
            continue

        messages.append({"role": "user", "content": line})
        reply = await _respond(ui, provider, messages)
        if reply:
            messages.append({"role": "assistant", "content": reply})

    ui.note("Goodbye 👋")


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
