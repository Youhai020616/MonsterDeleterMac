from __future__ import annotations

from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QApplication

from monster_deleter_mac.assets import (
    FLY_DURATION_MS,
    KICK_SPRITE,
    LEO_SPRITE,
    POINT_FRAME_INDICES,
    POINT_SPRITE,
    SPRITE_FPS,
    WALK_DURATION_MS,
    WALK_SPRITE,
    asset_path,
)
from monster_deleter_mac.trash import TrashService
from monster_deleter_mac.ui import MonsterOverlay, OverlayPhase, SpriteAnimator


def qt_app() -> QApplication:
    return QApplication.instance() or QApplication(["monster-deleter-test"])


def test_sprite_animator_loads_original_pointing_subset() -> None:
    app = qt_app()
    animator = SpriteAnimator()

    assert animator.load_spritesheet(
        asset_path(POINT_SPRITE), frame_indices=POINT_FRAME_INDICES
    )
    assert animator.source_frame_indices == POINT_FRAME_INDICES
    assert len(animator.frames) == 4

    animator.play(fps=SPRITE_FPS, loop=False)
    assert animator.timer.interval() == 125
    animator.stop()
    animator.deleteLater()
    app.processEvents()


def test_overlay_uses_upstream_stages_and_timings(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    app = qt_app()
    overlay = MonsterOverlay(None, TrashService(), demo=True)
    assert overlay.bubble.label.text() == "喂，是这个吗？\nwork"
    overlay.target_point = QPointF(700, 400)

    overlay._start_walk()
    assert overlay.phase is OverlayPhase.WALK
    assert overlay.animator.source_frame_indices == tuple(range(15))
    assert overlay.move_animation.duration() == WALK_DURATION_MS
    assert overlay.animator.timer.interval() == 125
    overlay.move_animation.stop()

    overlay._start_point()
    assert overlay.phase is OverlayPhase.POINT
    assert overlay.animator.source_frame_indices == POINT_FRAME_INDICES

    overlay._disconnect(overlay.animator.animationFinished)
    overlay.phase = OverlayPhase.ASK
    overlay._start_kick()
    assert overlay.phase is OverlayPhase.KICK
    assert overlay.animator.source_frame_indices == tuple(range(15))

    explosion_calls: list[bool] = []
    monkeypatch.setattr(overlay, "_trigger_explosion", lambda: explosion_calls.append(True))
    overlay._on_kick_frame(4)
    assert explosion_calls == []
    overlay._on_kick_frame(5)
    assert explosion_calls == [True]

    overlay.animator.stop()
    overlay._disconnect(overlay.animator.animationFinished)
    overlay._disconnect(overlay.animator.frameChanged)
    overlay._start_leo()
    assert overlay.phase is OverlayPhase.LEO
    assert overlay.animator.source_frame_indices == tuple(range(15))

    overlay.animator.stop()
    overlay._disconnect(overlay.animator.animationFinished)
    overlay._start_fly()
    assert overlay.phase is OverlayPhase.FLY
    assert overlay.animator.source_frame_indices == tuple(range(15))
    assert overlay.fly_animation.duration() == FLY_DURATION_MS

    overlay.fly_animation.stop()
    overlay.animator.stop()
    overlay.close()
    app.processEvents()


def test_stage_sprite_names_are_the_authorized_originals() -> None:
    assert WALK_SPRITE == "走路动效_spritesheet_transparent.png"
    assert POINT_SPRITE == "指着文件_spritesheet_transparent.png"
    assert KICK_SPRITE == "踹文件动效_spritesheet_transparent.png"
    assert LEO_SPRITE == "雷欧登场_spritesheet_transparent.png"
