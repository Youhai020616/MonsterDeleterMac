from __future__ import annotations

import argparse
import signal
import sys
from pathlib import Path
from typing import Sequence

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox

from .domain import LaunchRequest, TargetValidationError, validate_target
from .trash import TrashService
from .ui import MonsterOverlay


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="monster-deleter-mac",
        description="召唤原版大将怪兽，把确认后的文件安全移入 macOS 废纸篓。",
    )
    parser.add_argument("target", nargs="?", help="要处理的单个文件")
    parser.add_argument("--demo", action="store_true", help="播放演示，不处理文件")
    parser.add_argument("--dry-run", action="store_true", help="展示完整流程但不移动文件")
    parser.add_argument(
        "--auto-close-ms",
        type=int,
        default=None,
        help=argparse.SUPPRESS,
    )
    return parser


def parse_request(argv: Sequence[str] | None = None) -> LaunchRequest:
    namespace = build_parser().parse_args(argv)
    target = Path(namespace.target).expanduser() if namespace.target else None
    return LaunchRequest(
        target=target,
        demo=namespace.demo,
        dry_run=namespace.dry_run,
        auto_close_ms=namespace.auto_close_ms,
    )


def run_event_loop(app: QApplication, overlay: MonsterOverlay) -> int:
    """Run Qt while keeping terminal SIGINT/SIGTERM responsive."""
    signal_exit_code = [0]

    def request_exit(signal_number: int, _frame: object) -> None:
        signal_exit_code[0] = 128 + signal_number
        # Queue the request because Python can dispatch a signal halfway through
        # a paint/timer callback that still needs the widget instance.
        QTimer.singleShot(0, overlay.request_exit)

    watched_signals = (signal.SIGINT, signal.SIGTERM)
    previous_handlers = {
        signal_number: signal.getsignal(signal_number) for signal_number in watched_signals
    }
    for signal_number in watched_signals:
        signal.signal(signal_number, request_exit)

    # Qt's native event loop can otherwise prevent Python from dispatching signals.
    heartbeat = QTimer()
    heartbeat.setInterval(100)
    heartbeat.timeout.connect(lambda: None)
    heartbeat.start()

    try:
        qt_exit_code = int(app.exec())
        return signal_exit_code[0] or qt_exit_code
    finally:
        heartbeat.stop()
        for signal_number, previous_handler in previous_handlers.items():
            signal.signal(signal_number, previous_handler)


def main(argv: Sequence[str] | None = None) -> int:
    request = parse_request(argv)
    app = QApplication.instance() or QApplication(["monster-deleter-mac"])
    app.setApplicationName("MonsterDeleterMac")
    app.setFont(QFont("PingFang SC", 13))
    app.setQuitOnLastWindowClosed(True)

    target = request.target
    if target is None and not request.demo:
        selected, _ = QFileDialog.getOpenFileName(None, "选择要召唤怪兽处理的文件")
        if not selected:
            return 0
        target = Path(selected)

    try:
        safe_target = validate_target(target) if target is not None else None
    except TargetValidationError as error:
        print(str(error), file=sys.stderr)
        if request.auto_close_ms is None:
            QMessageBox.critical(None, "无法处理这个目标", str(error))
        return 2

    overlay = MonsterOverlay(
        safe_target,
        TrashService(),
        demo=request.demo,
        dry_run=request.dry_run,
        auto_close_ms=request.auto_close_ms,
    )
    overlay.show()
    if request.demo:
        print(
            "安全演示已打开：请用红色准星点击目标位置，再在动画中确认；按 Esc 或 Ctrl+C 退出。",
            flush=True,
        )
    return run_event_loop(app, overlay)


if __name__ == "__main__":
    raise SystemExit(main())
