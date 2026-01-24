from __future__ import annotations

import logging
from collections.abc import Callable

from gitcfg.core.exceptions import ScopeNotAvailableError
from gitcfg.core.models import ConfigScope, ConfigSnapshot
from gitcfg.core.parser import parse_git_config_output
from gitcfg.utils.subprocess_helper import CommandArgs, run_git_command
from gitcfg.utils.validators import ensure_scope_available

_LOGGER = logging.getLogger(__name__)

_CONFIG_LIST_ARGS: CommandArgs = ("config", "--list", "--show-scope", "--show-origin")


def read_config_snapshot(
    *,
    timeout: float | int | None = 10.0,
    runner: Callable[[CommandArgs, float | int | None], str] | None = None,
    require_scope: ConfigScope | None = None,
) -> ConfigSnapshot:
    """Retrieve the consolidated Git configuration as a :class:`ConfigSnapshot`."""

    output = _invoke_git_config(timeout=timeout, runner=runner)
    snapshot = parse_git_config_output(output)
    if require_scope is not None:
        if require_scope is ConfigScope.LOCAL and runner is None:
            _ensure_local_scope_available(snapshot, timeout)
        else:
            ensure_scope_available(require_scope, snapshot.scopes)

    _LOGGER.debug(
        "Loaded Git configuration snapshot with %d entries across %d scopes",
        len(snapshot.entries),
        len(snapshot.scopes),
    )
    return snapshot


def _invoke_git_config(
    *, timeout: float | int | None, runner: Callable[[CommandArgs, float | int | None], str] | None
) -> str:
    if runner is not None:
        return runner(_CONFIG_LIST_ARGS, timeout)

    result = run_git_command(_CONFIG_LIST_ARGS, timeout=timeout, check=True)
    return result.stdout


def _ensure_local_scope_available(snapshot: ConfigSnapshot, timeout: float | int | None) -> None:
    try:
        ensure_scope_available(ConfigScope.LOCAL, snapshot.scopes)
        return
    except ScopeNotAvailableError:
        pass

    probe = run_git_command(
        ("rev-parse", "--is-inside-work-tree"),
        timeout=timeout,
        check=False,
    )

    if probe.returncode == 0 and probe.stdout.strip().lower() == "true":
        return

    raise ScopeNotAvailableError("Local scope unavailable outside a Git repository.")


__all__ = ["read_config_snapshot"]
