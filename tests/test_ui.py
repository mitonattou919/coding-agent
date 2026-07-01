"""UI.stream_response のテスト（D8 確定表示 / D9 中断）。"""

from __future__ import annotations

import asyncio
from typing import AsyncIterator

from agent.ui import UI
from tests.conftest import run


async def _finite() -> AsyncIterator[str]:
    for chunk in ["Hello ", "stream ", "world"]:
        yield chunk


async def _partial_then_cancel() -> AsyncIterator[str]:
    yield "partial text"
    raise asyncio.CancelledError


def test_stream_response_returns_full_text() -> None:
    text = run(UI().stream_response(_finite()))
    assert text == "Hello stream world"


def test_stream_response_interrupted_returns_partial() -> None:
    # 途中で CancelledError（Ctrl+C 相当）が来ても、部分テキストを返す。
    text = run(UI().stream_response(_partial_then_cancel()))
    assert text == "partial text"


def test_stream_response_empty_stream() -> None:
    async def _empty() -> AsyncIterator[str]:
        return
        yield  # pragma: no cover

    text = run(UI().stream_response(_empty()))
    assert text == ""
