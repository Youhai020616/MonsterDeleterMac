from pathlib import Path

import pytest

from monster_deleter_mac.domain import (
    TargetValidationError,
    is_protected_path,
    validate_target,
)


def test_validate_target_accepts_regular_file(tmp_path: Path) -> None:
    target = tmp_path / "论文.txt"
    target.write_text("safe test data", encoding="utf-8")

    assert validate_target(target) == target.absolute()


def test_validate_target_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(TargetValidationError, match="不存在"):
        validate_target(tmp_path / "missing.txt")


def test_validate_target_rejects_directory(tmp_path: Path) -> None:
    with pytest.raises(TargetValidationError, match="不支持文件夹"):
        validate_target(tmp_path)


def test_validate_target_rejects_symbolic_link(tmp_path: Path) -> None:
    target = tmp_path / "target.txt"
    target.write_text("data", encoding="utf-8")
    link = tmp_path / "link.txt"
    link.symlink_to(target)

    with pytest.raises(TargetValidationError, match="符号链接"):
        validate_target(link)


@pytest.mark.parametrize(
    "path",
    [
        Path("/System/demo.txt"),
        Path("/Library/demo.txt"),
        Path("/usr/local/demo.txt"),
        Path("/private/etc/demo.txt"),
        Path("/private/var/db/demo.txt"),
    ],
)
def test_protected_paths(path: Path) -> None:
    assert is_protected_path(path)
