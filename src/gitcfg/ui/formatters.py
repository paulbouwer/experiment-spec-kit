from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from rich.json import JSON
from rich.panel import Panel
from rich.text import Text

from gitcfg.core.models import ConfigScope, ConfigSnapshot
from gitcfg.ui.themes import get_scope_style

_STATUS_STYLE_DEFAULT = "status.info"


def format_scope(scope: ConfigScope, label: str | None = None) -> Text:
    """Render a configuration scope using themed styling."""

    text = label if label is not None else scope.value
    return Text(text, style=get_scope_style(scope))


def status_panel(message: str, *, status: str = "info", title: str | None = None) -> Panel:
    """Create a standard status panel with theming applied."""

    style_name = f"status.{status}" if status else _STATUS_STYLE_DEFAULT
    return Panel(Text(message), border_style=style_name, title=title)


def dump_json(data: Any, *, indent: int = 2) -> str:
    """Serialize supported objects to JSON, handling Pydantic models and Rich types."""

    serializable = _prepare_for_json(data)
    return json.dumps(serializable, indent=indent, default=_json_default)


def to_rich_json(data: Any, *, indent: int = 2) -> JSON:
    """Wrap serialized JSON in a Rich JSON renderable."""

    return JSON(dump_json(data, indent=indent), indent=indent)


def snapshot_to_json(snapshot: ConfigSnapshot, *, indent: int = 2) -> JSON:
    """Serialize a configuration snapshot for JSON-friendly terminal output."""

    return to_rich_json(snapshot.model_dump(mode="json"), indent=indent)


def emphasize(text: str) -> Text:
    """Return emphasized text using the theme's title style."""

    return Text(text, style="title")


def _prepare_for_json(data: Any) -> Any:
    if isinstance(data, BaseModel):
        return data.model_dump(mode="json")
    return data


def _json_default(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, ConfigScope):
        return value.value
    if isinstance(value, set):
        return sorted(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


__all__ = [
    "dump_json",
    "emphasize",
    "format_scope",
    "snapshot_to_json",
    "status_panel",
    "to_rich_json",
]
