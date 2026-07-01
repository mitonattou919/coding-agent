"""入力まわりのテスト（D6 キーバインド / D11 履歴パス）。"""

from __future__ import annotations

from pathlib import Path

import pytest

from agent import input as input_mod


@pytest.fixture(autouse=True)
def _fake_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # 実ホームを汚さないよう HOME/USERPROFILE を一時ディレクトリへ。
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))


def test_history_path_location_and_dir_creation(tmp_path: Path) -> None:
    path = input_mod.history_path()
    assert path.name == "history"
    assert path.parent == tmp_path / ".coding-agent"
    assert path.parent.is_dir()  # 親ディレクトリが作られている


def _registered_keys(kb) -> set[tuple[str, ...]]:
    return {tuple(str(k) for k in b.keys) for b in kb.bindings}


def test_enter_submits_and_newline_keys_registered() -> None:
    keys = _registered_keys(input_mod._build_keybindings())
    assert ("Keys.ControlM",) in keys  # Enter = 送信
    assert ("Keys.ControlJ",) in keys  # Ctrl+J = 改行
    assert ("Keys.Escape", "Keys.ControlM") in keys  # Esc→Enter = 改行


def test_build_session_ok() -> None:
    # 例外なく構築できること（履歴・キーバインド込み）。
    assert input_mod.build_session() is not None
