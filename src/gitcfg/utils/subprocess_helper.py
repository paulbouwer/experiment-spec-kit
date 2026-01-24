from __future__ import annotations

import logging
import os
import shlex
import subprocess
from collections.abc import Mapping, Sequence

from gitcfg.core.exceptions import GitCommandError
from gitcfg.utils.validators import validate_timeout

_LOGGER = logging.getLogger(__name__)

CommandArgs = Sequence[str]


def _build_env(env: Mapping[str, str] | None) -> Mapping[str, str] | None:
    if env is None:
        return None

    merged = os.environ.copy()
    merged.update(env)
    return merged


def _log_command(command: Sequence[str]) -> None:
    if _LOGGER.isEnabledFor(logging.DEBUG):
        _LOGGER.debug("Running command: %s", shlex.join(command))


def run_git_command(
    args: CommandArgs,
    *,
    check: bool = True,
    timeout: float | int | None = 10.0,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a git command with consistent error handling."""

    command = ["git", *args]
    normalized_timeout = validate_timeout(timeout)
    _log_command(command)

    try:
        result = subprocess.run(  # noqa: S603 (shell=False)
            command,
            capture_output=True,
            text=True,
            timeout=normalized_timeout,
            env=_build_env(env),
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise GitCommandError(command, None, exc.stdout or "", exc.stderr or "", timeout=True) from exc
    except FileNotFoundError as exc:  # pragma: no cover - defensive for missing git
        raise GitCommandError(command, None, "", "git executable not found", timeout=False) from exc

    if check and result.returncode != 0:
        raise GitCommandError(command, result.returncode, result.stdout, result.stderr)

    return result


def ensure_git_available() -> None:
    """Verify that the git executable is present on PATH."""

    run_git_command(["--version"], check=True)


__all__ = ["CommandArgs", "ensure_git_available", "run_git_command"]
