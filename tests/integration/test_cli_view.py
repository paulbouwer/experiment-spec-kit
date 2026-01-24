from __future__ import annotations

import os
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from gitcfg.cli.app import get_app
from gitcfg.core.models import ConfigScope


def test_view_command_displays_scope_overrides(tmp_path: Path, monkeypatch) -> None:
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    init_result = subprocess.run(
        ["git", "init", "--initial-branch", "main"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    assert init_result.returncode == 0

    system_config = tmp_path / "system.gitconfig"
    global_config = tmp_path / "global.gitconfig"
    xdg_config = tmp_path / "xdg.gitconfig"

    system_config.write_text("[user]\nname=System User\n", encoding="utf-8")
    global_config.write_text(
        "[user]\nname=Global User\nemail=global@example.com\n",
        encoding="utf-8",
    )
    xdg_config.write_text("", encoding="utf-8")

    env = os.environ.copy()
    env.update(
        {
            "GIT_CONFIG_SYSTEM": str(system_config),
            "GIT_CONFIG_GLOBAL": str(global_config),
            "GIT_CONFIG_XDG": str(xdg_config),
            "HOME": str(tmp_path),
        },
    )

    subprocess.run(
        ["git", "config", "user.name", "Local User"],
        cwd=repo_dir,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "local@example.com"],
        cwd=repo_dir,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    runner = CliRunner()
    app = get_app()

    from gitcfg.cli.commands import view as view_module

    captured_snapshot = None
    original_read_snapshot = view_module.read_config_snapshot

    def _capture_snapshot(*, timeout=None, runner=None, require_scope=None):  # type: ignore[override]
        nonlocal captured_snapshot
        snapshot = original_read_snapshot(timeout=timeout, runner=runner, require_scope=require_scope)
        captured_snapshot = snapshot
        return snapshot

    monkeypatch.setattr(view_module, "read_config_snapshot", _capture_snapshot)

    original_cwd = os.getcwd()
    os.chdir(repo_dir)
    try:
        result = runner.invoke(app, ["view"], env=env, catch_exceptions=False)
    finally:
        os.chdir(original_cwd)

    assert result.exit_code == 0
    assert captured_snapshot is not None

    snapshot = captured_snapshot
    assert snapshot is not None  # for mypy

    local_scope_metadata = snapshot.scopes[ConfigScope.LOCAL]
    assert str(local_scope_metadata.path).endswith(".git/config")
    assert local_scope_metadata.is_writable is True

    user_config = snapshot.effective_map["user.name"]
    scopes = [entry.scope for entry in user_config.all_entries]
    assert scopes == [ConfigScope.SYSTEM, ConfigScope.GLOBAL, ConfigScope.LOCAL]

    system_entry = next(entry for entry in user_config.all_entries if entry.scope is ConfigScope.SYSTEM)
    assert system_entry.value == "System User"
    assert system_entry.is_active is False
    assert system_entry.overridden_by == [ConfigScope.LOCAL, ConfigScope.GLOBAL]

    global_entry = next(entry for entry in user_config.all_entries if entry.scope is ConfigScope.GLOBAL)
    assert global_entry.value == "Global User"
    assert global_entry.is_active is False
    assert global_entry.overridden_by == [ConfigScope.LOCAL]

    local_entry = user_config.active_entry
    assert local_entry.scope is ConfigScope.LOCAL
    assert local_entry.value == "Local User"

    email_config = snapshot.effective_map["user.email"]
    local_email = next(entry for entry in email_config.all_entries if entry.scope is ConfigScope.LOCAL)
    assert local_email.value == "local@example.com"
    assert local_email.is_active is True

    global_email = next(entry for entry in email_config.all_entries if entry.scope is ConfigScope.GLOBAL)
    assert global_email.value == "global@example.com"
    assert global_email.is_active is False
    assert global_email.overridden_by == [ConfigScope.LOCAL]
