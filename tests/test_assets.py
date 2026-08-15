from __future__ import annotations

import hashlib

import pytest
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QImageReader

from monster_deleter_mac.assets import (
    EXPLOSION_SPRITE,
    FLY_DURATION_MS,
    KICK_EXPLOSION_FRAME,
    POINT_FRAME_INDICES,
    SPRITE_COLUMNS,
    SPRITE_FPS,
    SPRITE_FRAME_COUNT,
    SPRITE_ROWS,
    UPSTREAM_ASSETS,
    UPSTREAM_COMMIT,
    WALK_DURATION_MS,
    asset_path,
)


@pytest.mark.parametrize("relative_path", UPSTREAM_ASSETS)
def test_authorized_upstream_asset_is_byte_exact(relative_path: str) -> None:
    expected = UPSTREAM_ASSETS[relative_path]
    path = asset_path(relative_path)

    assert path.stat().st_size == expected.size
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected.sha256


def test_all_spritesheets_keep_the_upstream_five_by_three_grid() -> None:
    for relative_path in UPSTREAM_ASSETS:
        if not relative_path.endswith("_spritesheet_transparent.png"):
            continue
        size = QImageReader(str(asset_path(relative_path))).size()
        assert size.isValid()
        assert size.width() % SPRITE_COLUMNS == 0
        assert size.height() % SPRITE_ROWS == 0

    assert QImageReader(str(asset_path(EXPLOSION_SPRITE))).size() == QSize(7200, 5760)


def test_animation_contract_matches_upstream_revision() -> None:
    assert UPSTREAM_COMMIT == "f2c43fd3c7efc6bb309d52d4f3884197fcaeaf40"
    assert SPRITE_FRAME_COUNT == 15
    assert SPRITE_FPS == 8
    assert POINT_FRAME_INDICES == (11, 12, 13, 14)
    assert WALK_DURATION_MS == 4500
    assert KICK_EXPLOSION_FRAME == 5
    assert FLY_DURATION_MS == 2000
