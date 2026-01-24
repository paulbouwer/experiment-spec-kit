from __future__ import annotations

from collections.abc import Iterable

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from gitcfg.core.categories import build_category_summaries
from gitcfg.core.models import ConfigEntry, ConfigScope, ConfigSnapshot
from gitcfg.ui.formatters import format_scope
from gitcfg.ui.themes import get_scope_style_name

_EM_DASH = "—"


def render_config_snapshot(
    snapshot: ConfigSnapshot,
    *,
    scope: ConfigScope | None = None,
    category_id: str | None = None,
) -> Panel | Group:
    """Return a Rich renderable representing the provided configuration snapshot."""

    table = build_config_table(snapshot, scope=scope, category_id=category_id)
    if table.row_count == 0:
        message = "No configuration entries available for the selected options."
        if scope:
            message += f" (scope: {scope.value})"
        if category_id:
            message += f" (category: {category_id})"
        return Panel(message, border_style="status.info", title="Empty Result")

    overview = build_scope_overview(snapshot, scope_filter=scope)
    return Group(overview, table)


def build_config_table(
    snapshot: ConfigSnapshot,
    *,
    scope: ConfigScope | None = None,
    category_id: str | None = None,
) -> Table:
    """Create a Rich table visualizing entries grouped by category."""

    table = Table(expand=True, show_lines=False, highlight=True)
    table.add_column("Category", style="title")
    table.add_column("Key", style="bold")
    table.add_column("Value")
    table.add_column("Scope")
    # table.add_column("Status")
    # table.add_column("Overrides")
    table.add_column("Origin", overflow="fold")
    table.add_column("Notes", overflow="fold")

    summaries = build_category_summaries(snapshot.entries)
    last_category_name: str | None = None
    last_key: str | None = None
    category_row_indices: list[int] = []
    for summary in summaries:
        if category_id and summary.category.id != category_id:
            continue

        filtered_entries = _filter_entries(summary.entries, scope)
        if not filtered_entries:
            continue

        starting_row_count = table.row_count
        for entry in filtered_entries:
            category_cell = summary.category.name if summary.category.name != last_category_name else ""
            if summary.category.name != last_category_name:
                last_key = None

            key_cell = entry.key if entry.key != last_key or summary.category.name != last_category_name else ""

            table.add_row(
                category_cell,
                key_cell,
                _format_value(entry),
                format_scope(entry.scope),
                # _format_status(entry),
                # _format_overrides(entry),
                Text(str(entry.origin), style="dim"),
                _format_notes(entry),
            )

            last_category_name = summary.category.name
            last_key = entry.key

        if table.row_count > starting_row_count:
            category_row_indices.append(table.row_count - 1)

    for row_index in category_row_indices[:-1]:
        table.rows[row_index].end_section = True

    return table


def build_scope_overview(
    snapshot: ConfigSnapshot,
    *,
    scope_filter: ConfigScope | None = None,
) -> Panel:
    """Render a concise overview of scope availability and writability."""

    table = Table(expand=True, box=None, show_header=True)
    table.add_column("Scope")
    table.add_column("Status")
    table.add_column("Config Path", overflow="fold")

    for scope in ConfigScope:
        style_name = get_scope_style_name(scope)
        scope_label = format_scope(scope)
        metadata = snapshot.scopes.get(scope)

        if metadata:
            status_label = "Writable" if metadata.is_writable else "Read-only"
            status_text = Text(status_label, style="status.success" if metadata.is_writable else "status.info")
            path_text = Text(str(metadata.path), style="dim")
        else:
            status_text = Text("Unavailable", style="status.warning")
            path_text = Text(_EM_DASH, style="dim")

        scope_label.stylize(style_name)
        if scope_filter and scope == scope_filter:
            scope_label.stylize("reverse")
        table.add_row(scope_label, status_text, path_text)

    return Panel(table, title="Scope Overview", border_style="title")


def _filter_entries(entries: Iterable[ConfigEntry], scope: ConfigScope | None) -> list[ConfigEntry]:
    if scope is None:
        return list(entries)
    return [entry for entry in entries if entry.scope == scope]


def _format_value(entry: ConfigEntry) -> Text:
    if entry.value == "":
        text = Text("∅", style="dim italic")
    else:
        sanitized_value = entry.value.replace("\n", "\\n")
        text = Text(sanitized_value)

    if entry.is_active:
        text.stylize(get_scope_style_name(entry.scope))
    else:
        text.stylize("dim")
        if entry.value:
            text.stylize("strike")

    return text


def _format_status(entry: ConfigEntry) -> Text:
    if entry.is_active:
        return Text("Active", style="status.success")

    if not entry.overridden_by:
        return Text("Inactive", style="status.info")

    overrides = ", ".join(scope.value for scope in entry.overridden_by)
    return Text(f"Overridden by {overrides}", style="status.warning")


def _format_overrides(entry: ConfigEntry) -> Text:
    if not entry.overridden_by:
        return Text(_EM_DASH, style="dim")

    parts: list[Text] = []
    for idx, scope in enumerate(entry.overridden_by):
        if idx:
            parts.append(Text(", ", style="dim"))
        parts.append(Text(scope.value, style=get_scope_style_name(scope)))

    text = Text()
    for part in parts:
        text.append(part)
    return text


def _format_notes(entry: ConfigEntry) -> Text:
    if not entry.annotations:
        return Text(_EM_DASH, style="dim")

    return Text("; ".join(entry.annotations), style="status.info")


__all__ = [
    "build_config_table",
    "build_scope_overview",
    "render_config_snapshot",
]
