from __future__ import annotations

from pathlib import Path
from typing import Protocol

from send2trash import send2trash

from .domain import validate_target


class TrashBackend(Protocol):
    def __call__(self, target: Path) -> None: ...


class Send2TrashBackend:
    def __call__(self, target: Path) -> None:
        send2trash(str(target))


class TrashService:
    """Revalidates the target immediately before moving it to Trash."""

    def __init__(self, backend: TrashBackend | None = None) -> None:
        self._backend = backend or Send2TrashBackend()

    def move(self, target: Path) -> Path:
        safe_target = validate_target(target)
        self._backend(safe_target)
        return safe_target

