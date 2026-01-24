from __future__ import annotations

from pathlib import Path

from gitcfg.core.models import ConfigEntry, ConfigScope, ConfigSnapshot, EffectiveConfig
from gitcfg.ui.tables import build_config_table


def _make_entry(
    *,
    scope: ConfigScope,
    is_active: bool,
    overridden_by: list[ConfigScope],
) -> ConfigEntry:
    return ConfigEntry(
        key="credential.helper",
        value="echo helper",
        scope=scope,
        origin=Path("/tmp/gitconfig"),
        category_id="credential-management",
        is_active=is_active,
        overridden_by=overridden_by,
    )


def test_build_config_table_suppresses_repeat_category_and_key() -> None:
    system_entry = _make_entry(scope=ConfigScope.SYSTEM, is_active=False, overridden_by=[ConfigScope.GLOBAL])
    global_entry = _make_entry(scope=ConfigScope.GLOBAL, is_active=True, overridden_by=[])

    snapshot = ConfigSnapshot(
        scopes={},
        entries=[system_entry, global_entry],
        effective_map={
            "credential.helper": EffectiveConfig(
                key="credential.helper",
                active_entry=global_entry,
                all_entries=[system_entry, global_entry],
            ),
        },
    )

    table = build_config_table(snapshot)

    assert len(table.rows) == 2

    category_cells = table.columns[0]._cells
    key_cells = table.columns[1]._cells

    assert category_cells == ["Credential Management", ""]
    assert key_cells == ["credential.helper", ""]


def test_build_config_table_adds_section_break_between_categories() -> None:
    user_entry = ConfigEntry(
        key="user.name",
        value="Example",
        scope=ConfigScope.GLOBAL,
        origin=Path("/tmp/gitconfig"),
        category_id="user-identity",
        is_active=True,
        overridden_by=[],
    )

    credential_entry = ConfigEntry(
        key="credential.helper",
        value="echo helper",
        scope=ConfigScope.GLOBAL,
        origin=Path("/tmp/gitconfig"),
        category_id="credential-management",
        is_active=True,
        overridden_by=[],
    )

    snapshot = ConfigSnapshot(
        scopes={},
        entries=[user_entry, credential_entry],
        effective_map={
            "user.name": EffectiveConfig(key="user.name", active_entry=user_entry, all_entries=[user_entry]),
            "credential.helper": EffectiveConfig(
                key="credential.helper",
                active_entry=credential_entry,
                all_entries=[credential_entry],
            ),
        },
    )

    table = build_config_table(snapshot)

    assert len(table.rows) == 2
    assert table.rows[0].end_section is True
    assert table.rows[1].end_section is False
