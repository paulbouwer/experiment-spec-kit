from __future__ import annotations

import logging
from dataclasses import dataclass

import typer
from rich.console import Console

from gitcfg.ui.themes import create_console

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class CLIContext:
    """Runtime context shared across Typer commands."""

    console: Console
    verbose: bool = False


def _configure_logging(verbose: bool) -> None:
    """Configure root logging level based on the verbose flag."""

    level = logging.DEBUG if verbose else logging.INFO
    root_logger = logging.getLogger()

    if not root_logger.handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    else:
        root_logger.setLevel(level)

    _LOGGER.debug("Logging configured at %s", logging.getLevelName(level))


app = typer.Typer(
    name="gitcfg",
    help="Explore and manage Git configuration with rich, scope-aware output.",
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    rich_markup_mode="rich",
)


@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Enable verbose diagnostic logging.",
        show_default=False,
    ),
) -> None:
    """Attach shared context for downstream Typer commands."""

    console = create_console()
    ctx.obj = CLIContext(console=console, verbose=verbose)
    _configure_logging(verbose)


def get_app() -> typer.Typer:
    """Return the configured Typer application instance."""

    return app


def run(prog_name: str | None = None) -> None:
    """Execute the gitcfg CLI."""

    app(prog_name=prog_name or "gitcfg")


__all__ = ["CLIContext", "app", "get_app", "run"]
