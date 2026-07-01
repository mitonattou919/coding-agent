"""テスト共通ヘルパ。

async テストは `pytest-asyncio` を入れず、`run()` で `asyncio.run` する方針
（依存を軽く保つ — docs/context.md の方針に沿う）。
"""

from __future__ import annotations

import asyncio
from typing import Awaitable, TypeVar

T = TypeVar("T")


def run(coro: Awaitable[T]) -> T:
    return asyncio.run(coro)  # type: ignore[arg-type]
