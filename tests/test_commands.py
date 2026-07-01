"""スラッシュコマンドのテスト（D9）。"""

from __future__ import annotations

from agent import commands
from agent.ui import UI


def test_is_command() -> None:
    assert commands.is_command("/help")
    assert commands.is_command("/exit now")
    assert not commands.is_command("hello")
    assert not commands.is_command("path/to/file")


def test_exit_and_quit_return_exit() -> None:
    ui = UI()
    assert commands.handle("/exit", ui, []) == "exit"
    assert commands.handle("/quit", ui, []) == "exit"


def test_clear_empties_messages() -> None:
    ui = UI()
    messages = [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}]
    assert commands.handle("/clear", ui, messages) == "handled"
    assert messages == []


def test_help_is_handled() -> None:
    ui = UI()
    assert commands.handle("/help", ui, []) == "handled"


def test_unknown_command_is_handled() -> None:
    ui = UI()
    assert commands.handle("/bogus", ui, []) == "handled"


def test_command_is_case_insensitive() -> None:
    ui = UI()
    assert commands.handle("/EXIT", ui, []) == "exit"
