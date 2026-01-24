"""Namespace for gitcfg Typer subcommands."""

from __future__ import annotations

import typer

from gitcfg.cli.commands.view import register as register_view_command


def register_commands(app: typer.Typer) -> None:
	"""Register all Typer commands with the application instance."""

	register_view_command(app)


__all__ = ["register_commands"]
