from __future__ import annotations

import os
import select
import signal
import subprocess
import sys
from pathlib import Path


def test_offscreen_demo_starts_and_stops() -> None:
    project_root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment["QT_QPA_PLATFORM"] = "offscreen"
    environment["PYTHONPATH"] = str(project_root / "src")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "monster_deleter_mac.cli",
            "--demo",
            "--auto-close-ms",
            "180",
        ],
        cwd=project_root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "安全演示已打开" in result.stdout


def test_terminal_sigint_stops_demo() -> None:
    project_root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment["QT_QPA_PLATFORM"] = "offscreen"
    environment["PYTHONPATH"] = str(project_root / "src")

    process = subprocess.Popen(
        [sys.executable, "-m", "monster_deleter_mac.cli", "--demo"],
        cwd=project_root,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        assert process.stdout is not None
        ready, _, _ = select.select([process.stdout], [], [], 5)
        assert ready, "demo did not print its startup message"
        assert "安全演示已打开" in process.stdout.readline()

        process.send_signal(signal.SIGINT)
        _, stderr = process.communicate(timeout=5)
        assert process.returncode == 130, stderr
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
