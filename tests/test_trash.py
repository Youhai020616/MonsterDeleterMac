from pathlib import Path

from monster_deleter_mac.trash import TrashService


class RecordingBackend:
    def __init__(self) -> None:
        self.targets: list[Path] = []

    def __call__(self, target: Path) -> None:
        self.targets.append(target)


def test_trash_service_revalidates_and_delegates(tmp_path: Path) -> None:
    target = tmp_path / "draft.txt"
    target.write_text("draft", encoding="utf-8")
    backend = RecordingBackend()

    moved = TrashService(backend).move(target)

    assert moved == target.absolute()
    assert backend.targets == [target.absolute()]
    assert target.exists(), "The fake backend must not remove the test file"

