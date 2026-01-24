from __future__ import annotations

import logging
import re
from collections.abc import Mapping
from typing import TYPE_CHECKING

from gitcfg.core.exceptions import ScopeNotAvailableError, ValidationError

_KEY_PATTERN = re.compile(r"^[A-Za-z0-9.\-]+$")
_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from gitcfg.core.models import ConfigScope, ScopeMetadata


def normalize_key(key: str) -> str:
    """Normalize a Git configuration key and validate that it is not empty."""

    normalized = key.strip()
    if not normalized:
        _LOGGER.debug("Rejecting empty Git configuration key")
        raise ValidationError("Git configuration key cannot be empty.")
    return normalized


def validate_key(key: str) -> str:
    """Ensure the provided Git configuration key matches the allowed pattern."""

    normalized = normalize_key(key)
    if not _KEY_PATTERN.fullmatch(normalized):
        _LOGGER.debug("Rejecting invalid Git key pattern: %s", key)
        raise ValidationError(
            "Git configuration keys may contain letters, numbers, dots, and hyphens.",
        )
    return normalized


def validate_timeout(timeout: float | int | None, *, minimum: float = 0.1) -> float | None:
    """Validate and normalize timeout values for subprocess execution."""

    if timeout is None:
        return None

    try:
        normalized = float(timeout)
    except (TypeError, ValueError) as exc:  # pragma: no cover - defensive programming
        raise ValidationError("Timeout must be a numeric value.") from exc

    if normalized < minimum:
        raise ValidationError(f"Timeout must be >= {minimum} seconds.")

    return normalized


def ensure_scope_available(scope: ConfigScope, metadata: Mapping[ConfigScope, ScopeMetadata] | None) -> None:
    """Verify that a scope exists within discovered metadata before use."""

    if metadata is None:
        return

    if scope not in metadata:
        _LOGGER.debug("Scope %s not present in metadata keys: %s", scope, list(metadata))
        raise ScopeNotAvailableError(f"Scope '{scope.value}' is not available in this context.")


def ensure_scope_writable(
    scope: ConfigScope,
    metadata: Mapping[ConfigScope, ScopeMetadata],
) -> None:
    """Validate that a scope is writable according to discovered metadata."""

    ensure_scope_available(scope, metadata)

    if not metadata[scope].is_writable:
        _LOGGER.debug("Scope %s is read-only", scope)
        raise ScopeNotAvailableError(
            f"Scope '{scope.value}' is read-only in the current environment.",
        )


__all__ = [
    "ensure_scope_available",
    "ensure_scope_writable",
    "normalize_key",
    "validate_key",
    "validate_timeout",
]
