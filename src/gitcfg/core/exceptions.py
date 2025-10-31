from __future__ import annotations

from collections.abc import Iterable, Sequence


class GitCfgError(Exception):
    """Base class for all gitcfg-specific errors."""


class ConfigurationError(GitCfgError):
    """Raised when configuration data is malformed or inconsistent."""


class ValidationError(GitCfgError):
    """Raised when user input fails validation rules."""


class CategoryNotFoundError(GitCfgError):
    """Raised when a requested configuration category is unknown."""


class ScopeNotAvailableError(GitCfgError):
    """Raised when a Git scope is unavailable in the current environment."""


class GitCommandError(GitCfgError):
    """Raised when invoking the git executable fails."""

    def __init__(
        self,
        command: Sequence[str],
        returncode: int | None,
        stdout: str,
        stderr: str,
        *,
        timeout: bool = False,
    ) -> None:
        self.command: tuple[str, ...] = tuple(command)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.timeout = timeout
        super().__init__(self._build_message())

    def _build_message(self) -> str:
        verb = "timed out" if self.timeout else "failed"
        pieces: list[str] = [f"git command {verb}: {' '.join(self.command)}"]

        if self.returncode is not None:
            pieces.append(f"exit code {self.returncode}")

        detail = (self.stderr or self.stdout or "").strip()
        if detail:
            pieces.append(detail)

        return " | ".join(pieces)

    def __str__(self) -> str:  # pragma: no cover - parent handles formatting
        return super().__str__()


def format_command(command: Iterable[str]) -> str:
    """Return a shell-friendly representation of a command sequence."""

    return " ".join(command)


__all__ = [
    "CategoryNotFoundError",
    "ConfigurationError",
    "GitCfgError",
    "GitCommandError",
    "ScopeNotAvailableError",
    "ValidationError",
    "format_command",
]
