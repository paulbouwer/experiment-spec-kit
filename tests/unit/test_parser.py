from __future__ import annotations

from pathlib import Path

import pytest

from gitcfg.core.models import ConfigScope
from gitcfg.core.parser import parse_git_config_output


def _git_line(scope: ConfigScope, path: Path, *, key: str, value: str) -> str:
    return f"{scope.value} file:{path} {key}={value}"


def test_parse_git_config_output_marks_active_scope_precedence(tmp_path: Path) -> None:
    system_config = tmp_path / "system.gitconfig"
    global_config = tmp_path / "global.gitconfig"
    local_config = tmp_path / "local.gitconfig"

    for config_path in (system_config, global_config, local_config):
        config_path.write_text("", encoding="utf-8")

    output = "\n".join(
        [
            _git_line(ConfigScope.SYSTEM, system_config, key="user.name", value="System User"),
            _git_line(ConfigScope.GLOBAL, global_config, key="user.name", value="Global User"),
            _git_line(ConfigScope.LOCAL, local_config, key="user.name", value="Local User"),
        ],
    )

    snapshot = parse_git_config_output(output)

    assert ConfigScope.LOCAL in snapshot.scopes
    local_metadata = snapshot.scopes[ConfigScope.LOCAL]
    assert local_metadata.path == local_config.resolve()
    assert local_metadata.is_writable is True

    effective = snapshot.effective_map["user.name"]
    scopes = [entry.scope for entry in effective.all_entries]
    assert scopes == [ConfigScope.SYSTEM, ConfigScope.GLOBAL, ConfigScope.LOCAL]

    system_entry = effective.all_entries[0]
    assert system_entry.is_active is False
    assert system_entry.overridden_by == [ConfigScope.LOCAL, ConfigScope.GLOBAL]

    global_entry = effective.all_entries[1]
    assert global_entry.is_active is False
    assert global_entry.overridden_by == [ConfigScope.LOCAL]

    local_entry = effective.all_entries[2]
    assert local_entry.is_active is True
    assert local_entry.overridden_by == []


@pytest.mark.parametrize(
    "config_key,expected_category",
    [
        ("remote.origin.url", "remote-settings"),
        ("branch.main.merge", "remote-settings"),
    ],
)
def test_parse_git_config_output_resolves_wildcard_categories(
    tmp_path: Path,
    config_key: str,
    expected_category: str,
) -> None:
    global_config = tmp_path / "global.gitconfig"
    global_config.write_text("", encoding="utf-8")

    output = _git_line(ConfigScope.GLOBAL, global_config, key=config_key, value="value")

    snapshot = parse_git_config_output(output)

    assert config_key in snapshot.effective_map
    entry = snapshot.effective_map[config_key].active_entry
    assert entry.category_id == expected_category
    assert entry.is_active is True
    assert entry.overridden_by == []


def test_parse_git_config_output_accepts_branch_key_with_slash(tmp_path: Path) -> None:
    global_config = tmp_path / "global.gitconfig"
    global_config.write_text("", encoding="utf-8")

    key = "branch.chore/bootstrap-repo-and-speckit.merge"
    value = "refs/heads/chore/bootstrap-repo-and-speckit"

    output = _git_line(ConfigScope.GLOBAL, global_config, key=key, value=value)

    snapshot = parse_git_config_output(output)

    assert key in snapshot.effective_map
    entry = snapshot.effective_map[key].active_entry
    assert entry.value == value
    assert entry.is_active is True
    assert entry.overridden_by == []
