from pathlib import Path

from monster_deleter_mac.cli import parse_request


def test_parse_demo_request() -> None:
    request = parse_request(["--demo", "--auto-close-ms", "250"])

    assert request.demo is True
    assert request.target is None
    assert request.auto_close_ms == 250


def test_parse_target_and_dry_run() -> None:
    request = parse_request(["--dry-run", "~/Desktop/test.txt"])

    assert request.dry_run is True
    assert request.target == Path("~/Desktop/test.txt").expanduser()

