from __future__ import annotations

import re
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from gitcfg.core.exceptions import ValidationError

_KEY_PATTERN = re.compile(r"^[A-Za-z0-9.\-]+$")
_SCOPE_PRECEDENCE = {
    "system": 0,
    "global": 1,
    "local": 2,
}


class ConfigScope(StrEnum):
    """Enumeration of Git configuration scopes ordered by precedence."""

    SYSTEM = "system"
    GLOBAL = "global"
    LOCAL = "local"

    @property
    def precedence(self) -> int:
        return _SCOPE_PRECEDENCE[self.value]

    @classmethod
    def from_git(cls, value: str) -> ConfigScope:
        normalized = value.strip().lower()
        try:
            return cls(normalized)
        except ValueError as exc:
            raise ValidationError(f"Unsupported Git scope '{value}'.") from exc


class ScopeMetadata(BaseModel):
    """Describes metadata about the availability of a Git configuration scope."""

    model_config = ConfigDict(extra="forbid")

    scope: ConfigScope
    path: Path
    is_writable: bool = Field(default=False)

    @field_validator("path")
    @classmethod
    def _ensure_path_exists(cls, value: Path) -> Path:
        expanded = value.expanduser()
        resolved = expanded if expanded.is_absolute() else expanded.resolve(strict=False)
        if not resolved.is_absolute():
            raise ValueError("Config path must be absolute.")
        if not resolved.exists():
            raise ValueError(f"Config path does not exist: {resolved}")
        return resolved


class ConfigEntry(BaseModel):
    """Represents a single Git configuration key/value pair from a specific scope."""

    model_config = ConfigDict(extra="forbid")

    key: str
    value: str
    scope: ConfigScope
    origin: Path
    category_id: str = Field(default="uncategorized")
    is_active: bool = Field(default=False)
    overridden_by: list[ConfigScope] = Field(default_factory=list)
    annotations: list[str] = Field(default_factory=list)

    @field_validator("key")
    @classmethod
    def _validate_key(cls, value: str) -> str:
        if not _KEY_PATTERN.fullmatch(value):
            raise ValueError("Invalid git configuration key format.")
        return value

    @field_validator("origin")
    @classmethod
    def _validate_origin(cls, value: Path) -> Path:
        if not value.is_absolute():
            return value.resolve(strict=False)
        return value

    @field_validator("overridden_by")
    @classmethod
    def _validate_overrides(cls, overrides: list[ConfigScope]) -> list[ConfigScope]:
        if not overrides:
            return overrides

        seen: set[ConfigScope] = set()
        for scope in overrides:
            if scope in seen:
                raise ValueError("Duplicate scope detected in overridden_by list.")
            seen.add(scope)
        return overrides

    @model_validator(mode="after")
    def _ensure_override_ordering(self) -> ConfigEntry:
        for override_scope in self.overridden_by:
            if override_scope.precedence <= self.scope.precedence:
                raise ValueError(
                    "Overrides must originate from higher-precedence scopes than the entry scope.",
                )
        return self


class EffectiveConfig(BaseModel):
    """Aggregated view of a Git configuration key across scopes."""

    model_config = ConfigDict(extra="forbid")

    key: str
    active_entry: ConfigEntry
    all_entries: list[ConfigEntry]

    @field_validator("key")
    @classmethod
    def _validate_key(cls, value: str) -> str:
        if not _KEY_PATTERN.fullmatch(value):
            raise ValueError("Invalid git configuration key format.")
        return value

    @model_validator(mode="after")
    def _ensure_consistency(self) -> EffectiveConfig:
        if self.active_entry not in self.all_entries:
            raise ValueError("Active entry must be present in all_entries list.")

        sorted_entries = sorted(self.all_entries, key=lambda entry: entry.scope.precedence)
        object.__setattr__(self, "all_entries", sorted_entries)
        return self


class ConfigCategory(BaseModel):
    """Metadata describing logical grouping of Git configuration keys."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    description: str
    keys: list[str] = Field(default_factory=list)
    related_categories: list[str] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def _validate_id(cls, value: str) -> str:
        if not value:
            raise ValueError("Category id cannot be empty.")
        return value


class CategoryBundle(BaseModel):
    """Higher-level grouping of categories for onboarding flows."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    description: str
    categories: list[ConfigCategory]

    @field_validator("id")
    @classmethod
    def _validate_id(cls, value: str) -> str:
        if not value:
            raise ValueError("Bundle id cannot be empty.")
        return value


class ConfigSnapshot(BaseModel):
    """Represents the full state of Git configuration for rendering and export."""

    model_config = ConfigDict(extra="forbid")

    scopes: dict[ConfigScope, ScopeMetadata]
    entries: list[ConfigEntry]
    effective_map: dict[str, EffectiveConfig]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def _validate_snapshot(self) -> ConfigSnapshot:
        seen: set[tuple[str, ConfigScope]] = set()
        for entry in self.entries:
            key_pair = (entry.key, entry.scope)
            if key_pair in seen:
                raise ValueError(
                    f"Duplicate configuration entry detected for {entry.key} at scope {entry.scope.value}.",
                )
            seen.add(key_pair)

        missing_keys = {entry.key for entry in self.entries} - set(self.effective_map)
        if missing_keys:
            missing = ", ".join(sorted(missing_keys))
            raise ValueError(f"Effective map missing keys: {missing}")

        return self

    def to_json(self, *, indent: int = 2) -> str:
        """Serialize the snapshot to JSON using the model's JSON encoder."""

        return self.model_dump_json(indent=indent)


class SetRequest(BaseModel):
    """Payload describing a configuration set operation."""

    model_config = ConfigDict(extra="forbid")

    key: str
    value: str
    scope: ConfigScope

    @field_validator("key")
    @classmethod
    def _validate_key(cls, value: str) -> str:
        if not _KEY_PATTERN.fullmatch(value):
            raise ValueError("Invalid git configuration key format.")
        return value

    @field_validator("value")
    @classmethod
    def _validate_value(cls, value: str) -> str:
        if value == "":
            raise ValueError("Configuration value cannot be empty.")
        return value


class UnsetRequest(BaseModel):
    """Payload describing a configuration unset operation."""

    model_config = ConfigDict(extra="forbid")

    key: str
    scope: ConfigScope

    @field_validator("key")
    @classmethod
    def _validate_key(cls, value: str) -> str:
        if not _KEY_PATTERN.fullmatch(value):
            raise ValueError("Invalid git configuration key format.")
        return value


__all__ = [
    "CategoryBundle",
    "ConfigCategory",
    "ConfigEntry",
    "ConfigScope",
    "ConfigSnapshot",
    "EffectiveConfig",
    "ScopeMetadata",
    "SetRequest",
    "UnsetRequest",
]
