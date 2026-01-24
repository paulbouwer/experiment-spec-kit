from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from fnmatch import fnmatchcase

from gitcfg.core.exceptions import CategoryNotFoundError
from gitcfg.core.models import CategoryBundle, ConfigCategory, ConfigEntry

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


@dataclass(frozen=True, slots=True)
class CategorySummary:
    """Aggregated view of configuration entries for a single category."""

    category: ConfigCategory
    entries: tuple[ConfigEntry, ...]
    active_count: int

    @property
    def total_entries(self) -> int:
        return len(self.entries)

    @property
    def has_entries(self) -> bool:
        return bool(self.entries)


@dataclass(frozen=True, slots=True)
class BundleSummary:
    """Aggregated view of categories for a curated bundle."""

    bundle: CategoryBundle
    categories: tuple[CategorySummary, ...]
    covered_categories: int
    active_categories: int

    @property
    def total_categories(self) -> int:
        return len(self.categories)

    @property
    def coverage_ratio(self) -> float:
        if not self.categories:
            return 0.0
        return self.covered_categories / self.total_categories

_DEFAULT_CATEGORIES: list[ConfigCategory] = [
    ConfigCategory(
        id="user-identity",
        name="User Identity",
        description="Identity details applied to commits and tags.",
        keys=["user.name", "user.email", "user.signingkey"],
        related_categories=["credential-management"],
    ),
    ConfigCategory(
        id="credential-management",
        name="Credential Management",
        description="Authentication helpers and credential caching controls.",
        keys=["credential.helper", "credential.useHttpPath"],
        related_categories=["user-identity"],
    ),
    ConfigCategory(
        id="commit-signing",
        name="Commit Signing",
        description="Enable and configure signing of commits.",
        keys=["user.signingkey", "commit.gpgsign", "gpg.format"],
        related_categories=["user-identity"],
    ),
    ConfigCategory(
        id="core-behavior",
        name="Core Behavior",
        description="Global Git behaviors that influence repository interactions.",
        keys=["core.*", "init.defaultbranch"],
        related_categories=[],
    ),
    ConfigCategory(
        id="remote-settings",
        name="Remote Settings",
        description="Remote and branch settings controlling fetch/push flows.",
        keys=["remote.*", "branch.*"],
        related_categories=[],
    ),
    ConfigCategory(
        id="custom-capabilities",
        name="Custom Capabilities",
        description="Custom capabilities available to the usre.",
        keys=["alias.*"],
        related_categories=[],
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
        id="secure-collaboration",
        name="Secure Collaboration",
        description="Settings that help avoid merge pitfalls and enforce secure defaults.",
        categories=[
            _CATEGORY_INDEX["commit-signing"],
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


def group_entries_by_category(entries: Iterable[ConfigEntry]) -> dict[str, tuple[ConfigEntry, ...]]:
    """Organize configuration entries by their resolved category identifier."""

    grouped: dict[str, list[ConfigEntry]] = {}
    for entry in entries:
        category_id = _resolve_entry_category(entry)
        grouped.setdefault(category_id, []).append(entry)

    for bucket in grouped.values():
        bucket.sort(key=_entry_sort_key)

    return {category_id: tuple(bucket) for category_id, bucket in grouped.items()}


def build_category_summaries(entries: Iterable[ConfigEntry]) -> list[CategorySummary]:
    """Produce ordered category summaries suitable for rendering or export."""

    grouped = group_entries_by_category(entries)
    summaries: list[CategorySummary] = []

    known_categories = tuple(get_categories())
    known_ids = {category.id for category in known_categories}

    for category in known_categories:
        summaries.append(_create_category_summary(category, grouped.get(category.id, ())))

    summaries.append(_create_category_summary(UNCATEGORIZED_CATEGORY, grouped.get(UNCATEGORIZED_CATEGORY.id, ())))

    for category_id, bucket in grouped.items():
        if category_id in known_ids or category_id == UNCATEGORIZED_CATEGORY.id:
            continue
        try:
            category = get_category(category_id)
        except CategoryNotFoundError:  # pragma: no cover - defensive fallback
            category = UNCATEGORIZED_CATEGORY
        summaries.append(_create_category_summary(category, bucket))

    return summaries


def build_bundle_summaries(
    category_summaries: Mapping[str, CategorySummary] | Sequence[CategorySummary],
    bundles: Sequence[CategoryBundle] | None = None,
) -> list[BundleSummary]:
    """Create bundle summaries referencing the provided category summaries."""

    if isinstance(category_summaries, Mapping):
        summary_map = dict(category_summaries)
    else:
        summary_map = {summary.category.id: summary for summary in category_summaries}

    bundle_definitions = tuple(bundles or get_bundles())
    results: list[BundleSummary] = []

    for bundle in bundle_definitions:
        category_summaries_for_bundle: list[CategorySummary] = []
        for category in bundle.categories:
            category_summary = summary_map.get(category.id)
            if category_summary is None:
                category_summary = CategorySummary(category=category, entries=tuple(), active_count=0)
            category_summaries_for_bundle.append(category_summary)

        covered = sum(1 for summary in category_summaries_for_bundle if summary.has_entries)
        active = sum(1 for summary in category_summaries_for_bundle if summary.active_count > 0)

        results.append(
            BundleSummary(
                bundle=bundle,
                categories=tuple(category_summaries_for_bundle),
                covered_categories=covered,
                active_categories=active,
            ),
        )

    return results


def _create_category_summary(category: ConfigCategory, entries: Iterable[ConfigEntry]) -> CategorySummary:
    entry_tuple = tuple(sorted(entries, key=_entry_sort_key))
    active_count = sum(1 for entry in entry_tuple if entry.is_active)
    return CategorySummary(category=category, entries=entry_tuple, active_count=active_count)


def _entry_sort_key(entry: ConfigEntry) -> tuple[str, int]:
    return (entry.key, entry.scope.precedence)


def _resolve_entry_category(entry: ConfigEntry) -> str:
    category_id = entry.category_id
    if category_id == UNCATEGORIZED_CATEGORY.id or category_id in _CATEGORY_INDEX:
        return category_id
    return resolve_category_id(entry.key)


__all__ = [
    "BundleSummary",
    "CategorySummary",
    "UNCATEGORIZED_CATEGORY",
    "build_bundle_summaries",
    "build_category_summaries",
    "get_bundles",
    "get_categories",
    "get_category",
    "get_category_for_key",
    "group_entries_by_category",
    "resolve_category_id",
]
