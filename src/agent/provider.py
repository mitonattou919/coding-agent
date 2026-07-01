"""応答プロバイダ（D7）。

`respond(messages) -> AsyncIterator[str]` を継ぎ目として定義する。
Phase 1 はモック実装を挿し、Phase 2 で Foundry 実装に差し替える。
"""

from __future__ import annotations

import asyncio
from typing import AsyncIterator, Protocol, runtime_checkable

Message = dict[str, str]


@runtime_checkable
class ResponseProvider(Protocol):
    """応答を逐次（ストリーミング）で返すものの共通インターフェース。"""

    def respond(self, messages: list[Message]) -> AsyncIterator[str]:
        ...


class MockProvider:
    """Phase 1 用スタブ。

    直近のユーザー発言をエコーしつつ、見出し・箇条書き・コードブロックを含む
    サンプル Markdown を、ストリーミング風に少しずつ返す。
    これにより UI の「ストリーム中プレーン → 確定後 Markdown」（D8）と
    スピナー・中断（Ctrl+C）を一通り検証できる。
    """

    def __init__(self, delay: float = 0.015) -> None:
        self._delay = delay

    async def respond(self, messages: list[Message]) -> AsyncIterator[str]:
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            "",
        )
        reply = self._compose(last_user)
        for token in self._tokenize(reply):
            await asyncio.sleep(self._delay)
            yield token

    def _compose(self, user_text: str) -> str:
        return (
            "## Mock response\n\n"
            "This is a Phase 1 stub response (no model connected yet). "
            "Echoing back what you sent:\n\n"
            f"> {user_text}\n\n"
            "It also returns a list and a code block so you can check "
            "streaming, the spinner, and final Markdown rendering.\n\n"
            "- Plain text while streaming\n"
            "- Rendered as Markdown once complete\n"
            "- `Ctrl+C` interrupts just the response (the app keeps running)\n\n"
            "```python\n"
            "def hello() -> str:\n"
            '    return "To be swapped for Foundry in Phase 2"\n'
            "```\n"
        )

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        # 空白を保ったまま単語＋区切りごとに分割し、トークン風に流す。
        import re

        return re.findall(r"\s+|\S+", text)
