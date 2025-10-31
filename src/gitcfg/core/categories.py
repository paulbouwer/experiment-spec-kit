from __future__ import annotations

from collections.abc import Sequence
from fnmatch import fnmatchcase

from gitcfg.core.exceptions import CategoryNotFoundError
from gitcfg.core.models import CategoryBundle, ConfigCategory

UNCATEGORIZED_CATEGORY = ConfigCategory(
    id="uncategorized",
    name="Uncategorized",
    description=(
        "Configuration keys without curated metadata. These should be reviewed to decide whether "
        "they warrant their own category or belong to an existing bundle."
    ),
    keys=[],
    related_categories=[],
)

_DEFAULT_CATEGORIES: list[ConfigCategory] = [
    ConfigCategory(
        id="user-identity",
        name="User Identity",
        description="Identity details applied to commits and tags.",
        keys=["user.name", "user.email", "user.signingkey"],
        related_categories=["credential-management", "safety"],
    ),
    ConfigCategory(
        id="core-behavior",
        name="Core Behavior",
        description="Global Git behaviors that influence repository interactions.",
        keys=["core.editor", "core.autocrlf", "core.ignorecase"],
        related_categories=["safety"],
    ),
    ConfigCategory(
        id="remote-settings",
        name="Remote Settings",
        description="Remote and branch settings controlling fetch/push flows.",
        keys=["remote.*", "branch.*"],
        related_categories=["core-behavior"],
    ),
    ConfigCategory(
        id="credential-management",
        name="Credential Management",
        description="Authentication helpers and credential caching controls.",
        keys=["credential.helper", "credential.useHttpPath"],
        related_categories=["user-identity"],
    ),
    ConfigCategory(
        id="safety",
        name="Safety",
        description="Safeguards that prevent data loss or enforce secure workflows.",
        keys=["commit.gpgSign", "pull.rebase"],
        related_categories=["user-identity", "core-behavior"],
    ),
]

_CATEGORY_INDEX: dict[str, ConfigCategory] = {
    category.id: category for category in _DEFAULT_CATEGORIES
}

_EXPLICIT_KEY_INDEX: dict[str, str] = {}
_WILDCARD_PATTERNS: list[tuple[str, str]] = []
for category in _DEFAULT_CATEGORIES:
    for key_pattern in category.keys:
        if "*" in key_pattern or "?" in key_pattern:
            _WILDCARD_PATTERNS.append((key_pattern, category.id))
        else:
            _EXPLICIT_KEY_INDEX[key_pattern] = category.id

_DEFAULT_BUNDLES: list[CategoryBundle] = [
    CategoryBundle(
        id="starter-identity",
        name="Starter Identity Setup",
        description="Recommended sequence for configuring author identity information.",
        categories=[
            _CATEGORY_INDEX["user-identity"],
            _CATEGORY_INDEX["credential-management"],
        ],
    ),
    CategoryBundle(
        id="safer-collaboration",
        name="Safer Collaboration",
        description="Settings that help avoid merge pitfalls and enforce secure defaults.",
        categories=[
            _CATEGORY_INDEX["safety"],
            _CATEGORY_INDEX["core-behavior"],
        ],
    ),
]


def get_categories() -> Sequence[ConfigCategory]:
    """Return the configured category metadata in definition order."""

    return tuple(_DEFAULT_CATEGORIES)


def get_category(category_id: str) -> ConfigCategory:
    """Lookup a category by identifier, raising if not found."""

    if category_id == UNCATEGORIZED_CATEGORY.id:
        return UNCATEGORIZED_CATEGORY

    try:
        return _CATEGORY_INDEX[category_id]
    except KeyError as exc:  # pragma: no cover - defensive guard
        raise CategoryNotFoundError(f"Unknown category id '{category_id}'.") from exc


def resolve_category_id(config_key: str) -> str:
    """Resolve a configuration key to a category identifier."""

    normalized_key = config_key.strip()
    if not normalized_key:
        return UNCATEGORIZED_CATEGORY.id

    if normalized_key in _EXPLICIT_KEY_INDEX:
        return _EXPLICIT_KEY_INDEX[normalized_key]

    for pattern, category_id in _WILDCARD_PATTERNS:
        if fnmatchcase(normalized_key, pattern):
            return category_id

    return UNCATEGORIZED_CATEGORY.id


def get_category_for_key(config_key: str) -> ConfigCategory:
    """Return the category instance that covers a given configuration key."""

    return get_category(resolve_category_id(config_key))


def get_bundles() -> Sequence[CategoryBundle]:
    """Return the default set of category bundles."""

    return tuple(_DEFAULT_BUNDLES)


__all__ = [
    "UNCATEGORIZED_CATEGORY",
    "get_bundles",
    "get_categories",
    "get_category",
    "get_category_for_key",
    "resolve_category_id",
]
