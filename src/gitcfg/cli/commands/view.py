from __future__ import annotations

from enum import Enum
from typing import Final

import typer

from gitcfg.cli.app import CLIContext
from gitcfg.core.categories import CategoryNotFoundError, get_category
from gitcfg.core.exceptions import GitCfgError, GitCommandError, ScopeNotAvailableError
from gitcfg.core.git_config import read_config_snapshot
from gitcfg.core.models import ConfigScope
from gitcfg.ui.formatters import snapshot_to_json, status_panel
from gitcfg.ui.tables import render_config_snapshot


class OutputFormat(str, Enum):
    PRETTY = "pretty"
    JSON = "json"


_SCOPE_OPTION = typer.Option(
    None,
    "--scope",
    help="Limit output to a single scope (system, global, or local).",
    case_sensitive=False,
)

_CATEGORY_OPTION = typer.Option(
    None,
    "--category",
    help="Restrict output to a configuration category (coming soon).",
)

_SEARCH_OPTION = typer.Option(
    None,
    "--search",
    help="Filter results by keyword (coming soon).",
)

_FORMAT_OPTION = typer.Option(
    OutputFormat.PRETTY,
    "--format",
    "-f",
    help="Select the output format.",
    case_sensitive=False,
)


def register(app: typer.Typer) -> None:
    """Register the view command with the shared Typer application."""

    app.command("view")(view)


def view(  # noqa: D401 - Typer provides help text
    ctx: typer.Context,
    scope: ConfigScope | None = _SCOPE_OPTION,
    category: str | None = _CATEGORY_OPTION,
    search: str | None = _SEARCH_OPTION,
    output_format: OutputFormat = _FORMAT_OPTION,
) -> None:
    """Display consolidated Git configuration data."""

    cli_ctx = ctx.ensure_object(CLIContext)
    console = cli_ctx.console

    category_id = None
    apply_category_filter: Final[bool] = False

    if category:
        try:
            category_id = get_category(category).id
        except CategoryNotFoundError as exc:
            console.print(status_panel(str(exc), status="error", title="Unknown category"))
            raise typer.Exit(code=3) from exc
        else:
            console.print(
                status_panel(
                    "Category filtering is not yet available. Showing all categories.",
                    status="warning",
                ),
            )

    if search:
        console.print(
            status_panel(
                "Search filtering is not yet available. Showing all entries.",
                status="warning",
            ),
        )

    required_scope = scope if scope is ConfigScope.LOCAL else None

    try:
        snapshot = read_config_snapshot(require_scope=required_scope)
    except ScopeNotAvailableError as exc:
        console.print(status_panel(str(exc), status="error", title="Scope Unavailable"))
        raise typer.Exit(code=4) from exc
    except GitCommandError as exc:
        console.print(status_panel(str(exc), status="error", title="Git Error"))
        raise typer.Exit(code=2) from exc
    except GitCfgError as exc:
        console.print(status_panel(str(exc), status="error", title="Error"))
        raise typer.Exit(code=2) from exc

    if output_format is OutputFormat.JSON:
        if scope or category_id or search:
            console.print(
                status_panel(
                    "JSON output currently ignores filters. Returning the full snapshot.",
                    status="warning",
                ),
            )
        console.print(snapshot_to_json(snapshot))
        return

    renderable = render_config_snapshot(
        snapshot,
        scope=scope,
        category_id=category_id if apply_category_filter else None,
    )
    console.print(renderable)


__all__ = ["register", "view", "OutputFormat"]
