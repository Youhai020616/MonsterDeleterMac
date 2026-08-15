#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from monster_deleter_mac.quick_action import (  # noqa: E402
    DEFAULT_ACTION_NAME,
    install_quick_action,
    uninstall_quick_action,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="安装或卸载 MonsterDeleterMac Finder 快速操作")
    parser.add_argument("--uninstall", action="store_true", help="卸载快速操作")
    parser.add_argument("--name", default=DEFAULT_ACTION_NAME, help="Finder 中显示的名称")
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path.home() / "Library" / "Services",
        help="工作流安装目录",
    )
    parser.add_argument(
        "--no-refresh",
        action="store_true",
        help="不刷新 macOS Services 缓存（主要用于测试）",
    )
    args = parser.parse_args()

    if args.uninstall:
        removed = uninstall_quick_action(
            args.destination,
            args.name,
            refresh_services=not args.no_refresh,
        )
        print("已卸载 Finder 快速操作。" if removed else "快速操作尚未安装。")
        return 0

    bundle = install_quick_action(
        PROJECT_ROOT,
        args.destination,
        args.name,
        refresh_services=not args.no_refresh,
    )
    print(f"已安装 Finder 快速操作：{bundle}")
    print("如果 Finder 没有立即显示，请在系统设置的 Finder 扩展中启用它。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

