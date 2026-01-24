"""Module entry point for the gitcfg CLI."""

from __future__ import annotations

from gitcfg.cli.app import run as run_app


def main() -> None:
    """Invoke the Typer-powered CLI application."""

    run_app()


if __name__ == "__main__":  # pragma: no cover - direct module execution
    main()
