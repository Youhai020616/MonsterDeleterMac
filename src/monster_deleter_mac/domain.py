from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class TargetValidationError(ValueError):
    """Raised when a requested target is unsafe or unsupported."""


PROTECTED_ROOTS = tuple(
    Path(value)
    for value in (
        "/System",
        "/Library",
        "/Applications",
        "/usr",
        "/bin",
        "/sbin",
        "/opt",
        "/private/etc",
        "/private/var/db",
        "/private/var/root",
        "/private/var/vm",
        "/private/var/protected",
    )
)


@dataclass(frozen=True, slots=True)
class LaunchRequest:
    target: Path | None
    demo: bool = False
    dry_run: bool = False
    auto_close_ms: int | None = None


def is_protected_path(path: Path) -> bool:
    resolved = path.resolve(strict=False)
    return any(resolved == root or root in resolved.parents for root in PROTECTED_ROOTS)


def validate_target(raw_target: str | Path) -> Path:
    target = Path(raw_target).expanduser().absolute()

    if not target.exists():
        raise TargetValidationError(f"文件不存在：{target}")
    if target.is_symlink():
        raise TargetValidationError("为避免误删链接目标，暂不支持符号链接。")
    if target.is_dir():
        raise TargetValidationError("当前版本只支持文件，不支持文件夹。")
    if not target.is_file():
        raise TargetValidationError("目标不是普通文件。")
    if is_protected_path(target):
        raise TargetValidationError("出于安全原因，不能处理系统保护路径中的文件。")

    return target
