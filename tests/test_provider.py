"""MockProvider のテスト（D7）。"""

from __future__ import annotations

from agent.provider import MockProvider
from tests.conftest import run


def _collect(messages: list[dict[str, str]]) -> str:
    async def _go() -> str:
        out = ""
        async for chunk in MockProvider(delay=0).respond(messages):
            out += chunk
        return out

    return run(_go())


def test_respond_streams_and_echoes_user_text() -> None:
    text = _collect([{"role": "user", "content": "echo me please"}])
    assert "Mock response" in text
    assert "echo me please" in text


def test_respond_uses_last_user_message() -> None:
    text = _collect(
        [
            {"role": "user", "content": "old message"},
            {"role": "assistant", "content": "..."},
            {"role": "user", "content": "newest message"},
        ]
    )
    assert "newest message" in text
    assert "old message" not in text


def test_respond_yields_multiple_chunks() -> None:
    async def _go() -> int:
        n = 0
        async for _ in MockProvider(delay=0).respond([{"role": "user", "content": "hi"}]):
            n += 1
        return n

    assert run(_go()) > 1


def test_tokenize_roundtrip_preserves_text() -> None:
    sample = "Hello,  world!\n\nNew line\tand tab."
    assert "".join(MockProvider._tokenize(sample)) == sample
