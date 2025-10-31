from __future__ import annotations

from functools import lru_cache

from rich.console import Console
from rich.style import Style
from rich.theme import Theme

from gitcfg.core.models import ConfigScope

_SCOPE_STYLE_MAP: dict[ConfigScope, Style] = {
    ConfigScope.SYSTEM: Style(color="cyan", bold=True),
    ConfigScope.GLOBAL: Style(color="green", bold=True),
    ConfigScope.LOCAL: Style(color="magenta", bold=True),
}

_BASE_THEME = Theme(
    {
        "scope.system": "bold cyan",
        "scope.global": "bold green",
        "scope.local": "bold magenta",
        "status.success": "bold green",
        "status.error": "bold red",
        "status.warning": "yellow",
        "status.info": "bright_white",
        "title": "bold white",
    }
)


@lru_cache(maxsize=1)
def get_theme() -> Theme:
    """Return the shared Rich theme for the CLI."""

    return _BASE_THEME


def create_console(*, no_color: bool = False) -> Console:
    """Create a Rich console configured with the gitcfg theme."""

    color_system = None if no_color else "auto"
    return Console(theme=get_theme(), color_system=color_system, highlight=True)


def get_scope_style(scope: ConfigScope) -> Style:
    """Get the Rich style associated with a configuration scope."""

    return _SCOPE_STYLE_MAP[scope]


def get_scope_style_name(scope: ConfigScope) -> str:
    """Return the theme style name for a configuration scope."""

    return f"scope.{scope.value}"


__all__ = [
    "create_console",
    "get_scope_style",
    "get_scope_style_name",
    "get_theme",
]
