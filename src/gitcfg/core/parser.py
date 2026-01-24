from __future__ import annotations

import logging
import os
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse

from gitcfg.core.categories import resolve_category_id
from gitcfg.core.exceptions import ConfigurationError
from gitcfg.core.models import (
    ConfigEntry,
    ConfigScope,
    ConfigSnapshot,
    EffectiveConfig,
    ScopeMetadata,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class _RawConfigRecord:
    scope: ConfigScope
    origin: Path
    key: str
    value: str
    file_origin: bool


def parse_git_config_output(output: str) -> ConfigSnapshot:
    """Parse the stdout from ``git config --list --show-scope --show-origin``."""

    records = _parse_records(output)
    if not records:
        return ConfigSnapshot(scopes={}, entries=[], effective_map={})

    entries, scopes = _build_entries(records)
    effective_map = _build_effective_map(entries)
    return ConfigSnapshot(scopes=scopes, entries=entries, effective_map=effective_map)


def _parse_records(output: str) -> list[_RawConfigRecord]:
    records: list[_RawConfigRecord] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        scope_token, origin_token, payload = _split_line(line)
        scope = ConfigScope.from_git(scope_token)
        origin, file_origin = _parse_origin(origin_token)
        key, value = _parse_key_value(payload)
        records.append(_RawConfigRecord(scope=scope, origin=origin, key=key, value=value, file_origin=file_origin))
    return records


def _split_line(line: str) -> tuple[str, str, str]:
    parts = line.split(None, 2)
    if len(parts) != 3:
        msg = f"Unexpected git config output format: {line!r}"
        _LOGGER.debug(msg)
        raise ConfigurationError(msg)
    return parts[0], parts[1], parts[2]


def _parse_origin(token: str) -> tuple[Path, bool]:
    cleaned = token.strip()
    if cleaned.startswith("file:"):
        parsed = urlparse(cleaned)
        if parsed.scheme != "file":
            raise ConfigurationError(f"Unsupported origin scheme in git output: {token!r}")
        raw_path = unquote(parsed.path)
        if parsed.netloc:
            raw_path = f"{parsed.netloc}{raw_path}"
        if not raw_path:
            raise ConfigurationError(f"Origin path missing in git output: {token!r}")
        if os.name == "nt" and raw_path.startswith("/") and len(raw_path) > 2 and raw_path[2] == ":":
            raw_path = raw_path.lstrip("/")
        path = Path(raw_path).expanduser()
        if not path.is_absolute():
            path = path.resolve(strict=False)
        return path, True

    sanitized = cleaned.strip('"')
    return Path(sanitized), False


def _parse_key_value(payload: str) -> tuple[str, str]:
    if "=" in payload:
        key, value = payload.split("=", 1)
    else:
        key, value = payload, ""
    key = key.strip()
    if not key:
        raise ConfigurationError("Encountered git configuration entry with empty key.")
    return key, value.rstrip("\n")


def _build_entries(records: Sequence[_RawConfigRecord]) -> tuple[list[ConfigEntry], dict[ConfigScope, ScopeMetadata]]:
    key_scope_map: dict[tuple[str, ConfigScope], _RawConfigRecord] = {}
    duplicate_counts: dict[tuple[str, ConfigScope], int] = {}
    scope_candidates: dict[ConfigScope, list[Path]] = {}

    for record in records:
        key = (record.key, record.scope)
        duplicate_counts[key] = duplicate_counts.get(key, 0) + 1
        key_scope_map[key] = record

        if record.file_origin:
            scope_candidates.setdefault(record.scope, []).append(record.origin)

    entries_by_key: dict[str, list[ConfigEntry]] = {}
    for (config_key, scope), record in key_scope_map.items():
        annotations: list[str] = []
        duplicate_total = duplicate_counts[(config_key, scope)]
        if duplicate_total > 1:
            annotations.append(
                f"{duplicate_total} values defined at {scope.value} scope; using the most recent definition.",
            )
        category_id = resolve_category_id(record.key)
        entry = ConfigEntry(
            key=record.key,
            value=record.value,
            scope=record.scope,
            origin=record.origin,
            category_id=category_id,
            annotations=annotations,
        )
        entries_by_key.setdefault(record.key, []).append(entry)

    normalized_entries: list[ConfigEntry] = []

    for _key, entry_list in entries_by_key.items():
        ordered = sorted(entry_list, key=lambda item: item.scope.precedence)
        updated: list[ConfigEntry] = []
        for index, entry in enumerate(ordered):
            remaining = ordered[index + 1 :]
            higher_scopes = [candidate.scope for candidate in reversed(remaining)]
            update_payload: dict[str, object] = {"overridden_by": higher_scopes}
            if not higher_scopes:
                update_payload["is_active"] = True
            updated.append(entry.model_copy(update=update_payload))
        normalized_entries.extend(updated)

    entries_sorted = sorted(
        normalized_entries,
        key=lambda item: (item.category_id, item.key, item.scope.precedence),
    )

    metadata: dict[ConfigScope, ScopeMetadata] = {}
    for scope, candidates in scope_candidates.items():
        for candidate in candidates:
            if not candidate.exists():
                continue
            is_writable = os.access(candidate, os.W_OK)
            try:
                metadata[scope] = ScopeMetadata(scope=scope, path=candidate, is_writable=is_writable)
                break
            except ValueError:
                _LOGGER.debug("Skipping invalid scope path for %s: %s", scope, candidate)
        else:
            _LOGGER.debug("No valid configuration file path discovered for scope %s", scope)

    return entries_sorted, metadata


def _build_effective_map(entries: Iterable[ConfigEntry]) -> dict[str, EffectiveConfig]:
    grouped: dict[str, list[ConfigEntry]] = {}
    for entry in entries:
        grouped.setdefault(entry.key, []).append(entry)

    effective: dict[str, EffectiveConfig] = {}
    for key, key_entries in grouped.items():
        active_entry = next((item for item in key_entries if item.is_active), None)
        if active_entry is None:
            raise ConfigurationError(f"No active entry detected for key '{key}'.")
        effective[key] = EffectiveConfig(key=key, active_entry=active_entry, all_entries=key_entries)
    return effective


__all__ = ["parse_git_config_output"]
