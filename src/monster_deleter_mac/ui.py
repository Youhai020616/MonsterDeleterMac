from __future__ import annotations

import os
from enum import Enum, auto
from pathlib import Path
from typing import Sequence

os.environ.setdefault(
    "QT_LOGGING_RULES",
    "qt.multimedia.ffmpeg.*=false;qt.multimedia.ffmpeg=false",
)

from PyQt6.QtCore import (
    QEasingCurve,
    QPoint,
    QPointF,
    QPropertyAnimation,
    QRectF,
    Qt,
    QTimer,
    QUrl,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QColor,
    QCursor,
    QImage,
    QKeySequence,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QShortcut,
    QTransform,
)
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .assets import (
    BGM_AUDIO,
    EXPLOSION_AUDIO,
    EXPLOSION_HEIGHT,
    EXPLOSION_SPRITE,
    FLY_DURATION_MS,
    FLY_SPRITE,
    KICK_EXPLOSION_FRAME,
    KICK_SPRITE,
    LEO_SPRITE,
    MONSTER_HEIGHT,
    POINT_FRAME_INDICES,
    POINT_SPRITE,
    SELECTION_BACKGROUND,
    SPRITE_COLUMNS,
    SPRITE_FPS,
    SPRITE_ROWS,
    VOICE_AUDIO,
    WALK_DURATION_MS,
    WALK_SPRITE,
    asset_path,
)
from .trash import TrashService


class OverlayPhase(Enum):
    TARGETING = auto()
    WALK = auto()
    POINT = auto()
    ASK = auto()
    KICK = auto()
    LEO = auto()
    FLY = auto()


class SpriteAnimator(QLabel):
    """The upstream 5x3 spritesheet player, ported directly to PyQt6/macOS."""

    animationFinished = pyqtSignal()
    frameChanged = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.frames: list[QPixmap] = []
        self.source_frame_indices: tuple[int, ...] = ()
        self.current_frame = 0
        self.loop = True
        self.flip_horizontal = False
        self.is_playing = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)

    def load_spritesheet(
        self,
        filepath: Path,
        *,
        cols: int = SPRITE_COLUMNS,
        rows: int = SPRITE_ROWS,
        target_height: int = MONSTER_HEIGHT,
        frame_indices: Sequence[int] | None = None,
    ) -> bool:
        self.stop()
        image = QImage(str(filepath))
        if image.isNull():
            return False
        if image.width() % cols or image.height() % rows:
            raise ValueError(f"精灵表尺寸不能被 {cols}x{rows} 整除：{filepath}")

        pixmap = QPixmap.fromImage(image)
        frame_width = pixmap.width() // cols
        frame_height = pixmap.height() // rows
        all_frames = [
            pixmap.copy(column * frame_width, row * frame_height, frame_width, frame_height)
            .scaledToHeight(target_height, Qt.TransformationMode.SmoothTransformation)
            for row in range(rows)
            for column in range(cols)
        ]

        indices = tuple(frame_indices) if frame_indices is not None else tuple(range(len(all_frames)))
        if any(index < 0 or index >= len(all_frames) for index in indices):
            raise IndexError(f"精灵帧索引越界：{filepath}")

        self.source_frame_indices = indices
        self.frames = [all_frames[index] for index in indices]
        self.current_frame = 0
        if self.frames:
            self.resize(self.frames[0].size())
            self._update_frame()
        return bool(self.frames)

    def set_flip(self, flip: bool) -> None:
        self.flip_horizontal = flip
        self._update_frame()

    def play(self, *, fps: int = SPRITE_FPS, loop: bool = True) -> None:
        if not self.frames:
            return
        self.loop = loop
        self.current_frame = 0
        self.is_playing = True
        self.timer.start(1000 // fps)
        self._update_frame()

    def stop(self) -> None:
        self.timer.stop()
        self.is_playing = False

    def next_frame(self) -> None:
        if not self.frames:
            return

        self.current_frame += 1
        if self.current_frame >= len(self.frames):
            if self.loop:
                self.current_frame = 0
            else:
                self.current_frame = len(self.frames) - 1
                self.stop()
                self._update_frame()
                self.frameChanged.emit(self.current_frame)
                self.animationFinished.emit()
                return

        self._update_frame()
        self.frameChanged.emit(self.current_frame)

    def _update_frame(self) -> None:
        if not self.frames:
            return
        frame = self.frames[self.current_frame]
        if self.flip_horizontal:
            frame = frame.transformed(
                QTransform().scale(-1, 1),
                Qt.TransformationMode.SmoothTransformation,
            )
        self.setPixmap(frame)


class BubbleWidget(QWidget):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 15)
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(
            """
            QLabel {
                color: #1c1c1e;
                padding: 15px 30px;
                font-family: 'PingFang SC', 'Segoe UI', 'Microsoft YaHei', sans-serif;
                font-size: 20px;
                font-weight: 600;
            }
            """
        )
        layout.addWidget(self.label)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)
        self.adjustSize()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 240))

        body_height = self.height() - 15
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self.width(), body_height), 20, 20)
        tail = QPainterPath()
        tail.moveTo(self.width() / 2 - 15, body_height)
        tail.lineTo(self.width() / 2, self.height())
        tail.lineTo(self.width() / 2 + 15, body_height)
        path.addPath(tail)
        painter.drawPath(path)


class ChoicesWidget(QWidget):
    choiceMade = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QHBoxLayout(self)
        layout.setSpacing(15)
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 240);
                color: #1c1c1e;
                border: 1px solid #e5e5ea;
                border-radius: 18px;
                padding: 12px 25px;
                font-family: 'PingFang SC', 'Segoe UI', 'Microsoft YaHei', sans-serif;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #007aff;
                color: #ffffff;
                border: 1px solid #007aff;
            }
            QPushButton:pressed {
                background-color: #005bb5;
                color: #ffffff;
            }
        """

        for text in ("是的", "嘤嘤嘤就是这个"):
            button = QPushButton(text)
            button.setStyleSheet(button_style)
            shadow = QGraphicsDropShadowEffect(button)
            shadow.setBlurRadius(15)
            shadow.setOffset(0, 5)
            shadow.setColor(QColor(0, 0, 0, 30))
            button.setGraphicsEffect(shadow)
            button.clicked.connect(self._choose)
            layout.addWidget(button)
        self.adjustSize()

    def _choose(self) -> None:
        self.hide()
        self.choiceMade.emit()


class MonsterOverlay(QWidget):
    """macOS host for the authorized upstream monster animation sequence."""

    def __init__(
        self,
        target: Path | None,
        trash_service: TrashService,
        *,
        demo: bool = False,
        dry_run: bool = False,
        auto_close_ms: int | None = None,
    ) -> None:
        super().__init__()
        self.target = target
        self.trash_service = trash_service
        self.demo = demo
        self.dry_run = dry_run
        self.phase = OverlayPhase.TARGETING
        self.target_point: QPointF | None = None
        self.trash_attempted = False
        self.status_message = ""
        self._bg_opacity = 0.0
        self._shutdown_started = False
        self._shutdown_ready = False
        self._retiring_players: list[QMediaPlayer] = []

        self.setWindowTitle("MonsterDeleterMac")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        cursor = QCursor.pos()
        screen = QApplication.screenAt(cursor) or QApplication.primaryScreen()
        if screen is None:
            self.setGeometry(0, 0, 960, 640)
        else:
            self.setGeometry(screen.geometry())

        self.selection_image = QImage(str(asset_path(SELECTION_BACKGROUND)))
        self.animator = SpriteAnimator(self)
        self.animator.hide()
        self.explosion_animator = SpriteAnimator(self)
        self.explosion_animator.hide()

        target_name = target.name if target is not None else "work"
        self.bubble = BubbleWidget(f"喂，是这个吗？\n{target_name}", self)
        self.bubble.hide()
        self.choices = ChoicesWidget(self)
        self.choices.choiceMade.connect(self._start_kick)
        self.choices.hide()

        self.bgm_player: QMediaPlayer | None = None
        self.sfx_player: QMediaPlayer | None = None
        self.explosion_player: QMediaPlayer | None = None
        self._init_audio()

        self.escape_shortcut = QShortcut(QKeySequence("Esc"), self)
        self.escape_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.escape_shortcut.activated.connect(self._cancel)

        self._init_targeting_ui()
        if auto_close_ms is not None:
            QTimer.singleShot(max(50, auto_close_ms), self._auto_close)

    @pyqtProperty(float)
    def bg_opacity(self) -> float:
        return self._bg_opacity

    @bg_opacity.setter
    def bg_opacity(self, value: float) -> None:
        self._bg_opacity = value
        self.update()

    def _init_audio(self) -> None:
        if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
            return

        self.bgm_player = self._create_player(BGM_AUDIO, 0.5)
        self.bgm_player.mediaStatusChanged.connect(self._loop_bgm)
        self.sfx_player = self._create_player(VOICE_AUDIO, 1.0)
        self.explosion_player = self._create_player(EXPLOSION_AUDIO, 0.3)

    def _create_player(self, relative_path: str, volume: float) -> QMediaPlayer:
        player = QMediaPlayer(self)
        audio = QAudioOutput(player)
        audio.setVolume(volume)
        player.setAudioOutput(audio)
        player.setSource(QUrl.fromLocalFile(str(asset_path(relative_path))))
        return player

    def _loop_bgm(self, status: QMediaPlayer.MediaStatus) -> None:
        if status is QMediaPlayer.MediaStatus.EndOfMedia and self.bgm_player is not None:
            self.bgm_player.setPosition(0)
            self.bgm_player.play()

    def _init_targeting_ui(self) -> None:
        cursor_size = 40
        cursor_pixmap = QPixmap(cursor_size, cursor_size)
        cursor_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(cursor_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        center = cursor_size // 2
        radius = 12
        painter.drawEllipse(center - radius, center - radius, radius * 2, radius * 2)
        painter.drawLine(center, 0, center, center - 4)
        painter.drawLine(center, center + 4, center, cursor_size)
        painter.drawLine(0, center, center - 4, center)
        painter.drawLine(center + 4, center, cursor_size, center)
        painter.end()
        self.setCursor(QCursor(cursor_pixmap, center, center))

        self.fade_in_animation = QPropertyAnimation(self, b"bg_opacity")
        self.fade_in_animation.setDuration(800)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(0.35)
        self.fade_in_animation.start()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if self._bg_opacity <= 0.01:
            return

        painter = QPainter(self)
        if not self.selection_image.isNull():
            scaled_image = self.selection_image.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.setOpacity(self._bg_opacity)
            painter.drawImage(
                (self.width() - scaled_image.width()) // 2,
                (self.height() - scaled_image.height()) // 2,
                scaled_image,
            )
        else:
            painter.setOpacity(self._bg_opacity)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 160))

        painter.setOpacity(min(1.0, self._bg_opacity / 0.35))
        painter.setPen(QColor(255, 255, 255))
        font = painter.font()
        font.setPointSize(30)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "请选择你要摧毁的文件")

    def showEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().showEvent(event)
        self.raise_()
        self.activateWindow()
        self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    def mousePressEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if (
            self.phase is OverlayPhase.TARGETING
            and self.target_point is None
            and event.button() is Qt.MouseButton.LeftButton
        ):
            self._select_target(event.position())
            return
        super().mousePressEvent(event)

    def _select_target(self, point: QPointF) -> None:
        self.target_point = point
        self.unsetCursor()
        self.fade_out_animation = QPropertyAnimation(self, b"bg_opacity")
        self.fade_out_animation.setDuration(500)
        self.fade_out_animation.setStartValue(self._bg_opacity)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.finished.connect(self._start_walk)
        self.fade_out_animation.start()

    def _load_monster(
        self,
        sprite_name: str,
        *,
        frame_indices: Sequence[int] | None = None,
    ) -> None:
        loaded = self.animator.load_spritesheet(
            asset_path(sprite_name),
            target_height=MONSTER_HEIGHT,
            frame_indices=frame_indices,
        )
        if not loaded:
            raise RuntimeError(f"无法加载原版精灵表：{sprite_name}")

    @staticmethod
    def _disconnect(signal: object) -> None:
        try:
            signal.disconnect()  # type: ignore[attr-defined]
        except (TypeError, RuntimeError):
            pass

    def _start_walk(self) -> None:
        if self.target_point is None:
            return
        self.phase = OverlayPhase.WALK
        if self.bgm_player is not None:
            self.bgm_player.play()

        self._load_monster(WALK_SPRITE)
        start_x = -self.animator.width()
        start_y = int(self.target_point.y()) - self.animator.height() // 2 + 50
        end_x = int(self.target_point.x()) - self.animator.width() - 30
        self.animator.set_flip(False)
        self.animator.move(start_x, start_y)
        self.animator.show()
        self.animator.play(fps=SPRITE_FPS, loop=True)

        self.move_animation = QPropertyAnimation(self.animator, b"pos")
        self.move_animation.setDuration(WALK_DURATION_MS)
        self.move_animation.setStartValue(QPoint(start_x, start_y))
        self.move_animation.setEndValue(QPoint(end_x, start_y))
        self.move_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.move_animation.finished.connect(self._start_point)
        self.move_animation.start()

    def _start_point(self) -> None:
        self.phase = OverlayPhase.POINT
        if self.sfx_player is not None:
            self.sfx_player.play()
        self._load_monster(POINT_SPRITE, frame_indices=POINT_FRAME_INDICES)
        self._disconnect(self.animator.animationFinished)
        self.animator.animationFinished.connect(self._show_dialog)
        self.animator.play(fps=SPRITE_FPS, loop=False)

    def _show_dialog(self) -> None:
        self.phase = OverlayPhase.ASK
        self._disconnect(self.animator.animationFinished)
        self.bubble.adjustSize()
        self.choices.adjustSize()

        bubble_x = self.animator.x() + self.animator.width() // 2 - 80
        bubble_y = self.animator.y() - 60
        choices_x = self.animator.x() + self.animator.width() // 2 - 130
        choices_y = self.animator.y() + self.animator.height() - 20
        self.bubble.move(self._clamp_x(bubble_x, self.bubble.width()), max(8, bubble_y))
        self.choices.move(self._clamp_x(choices_x, self.choices.width()), choices_y)
        self.bubble.show()
        self.bubble.raise_()
        self.choices.show()
        self.choices.raise_()

    def _clamp_x(self, x: int, widget_width: int) -> int:
        return min(max(8, x), max(8, self.width() - widget_width - 8))

    def _start_kick(self) -> None:
        if self.phase is not OverlayPhase.ASK:
            return
        self.phase = OverlayPhase.KICK
        self.bubble.hide()
        self._disconnect(self.animator.animationFinished)
        self._disconnect(self.animator.frameChanged)
        self._load_monster(KICK_SPRITE)
        self.animator.animationFinished.connect(self._on_kick_finished)
        self.animator.frameChanged.connect(self._on_kick_frame)
        self.animator.play(fps=SPRITE_FPS, loop=False)

    def _on_kick_frame(self, frame_index: int) -> None:
        if frame_index == KICK_EXPLOSION_FRAME:
            self._trigger_explosion()

    def _trigger_explosion(self) -> None:
        if self.target_point is None:
            return
        if self.explosion_player is not None:
            self.explosion_player.play()
        loaded = self.explosion_animator.load_spritesheet(
            asset_path(EXPLOSION_SPRITE),
            target_height=EXPLOSION_HEIGHT,
        )
        if not loaded:
            raise RuntimeError("无法加载原版爆炸精灵表")

        explosion_x = int(self.target_point.x()) - self.explosion_animator.width() // 2
        explosion_y = int(self.target_point.y()) - self.explosion_animator.height() // 2 - 40
        self.explosion_animator.move(explosion_x, explosion_y)
        self.explosion_animator.show()
        self.explosion_animator.raise_()
        self._disconnect(self.explosion_animator.animationFinished)
        self.explosion_animator.animationFinished.connect(self.explosion_animator.hide)
        self.explosion_animator.play(fps=SPRITE_FPS, loop=False)
        self._move_target_to_trash()

    def _move_target_to_trash(self) -> None:
        if self.trash_attempted:
            return
        self.trash_attempted = True
        try:
            if self.demo:
                self.status_message = "演示完成：没有操作任何文件"
            elif self.dry_run:
                self.status_message = "Dry-run 完成：文件保持原样"
            elif self.target is None:
                raise RuntimeError("缺少目标文件")
            else:
                self.trash_service.move(self.target)
                self.status_message = "已安全移入废纸篓，可随时恢复"
            print(self.status_message, flush=True)
        except Exception as error:  # Surface the backend failure without crashing the animation.
            self.status_message = f"操作失败：{error}"
            print(self.status_message, flush=True)

    def _on_kick_finished(self) -> None:
        self._disconnect(self.animator.animationFinished)
        self._disconnect(self.animator.frameChanged)
        self._start_leo()

    def _start_leo(self) -> None:
        self.phase = OverlayPhase.LEO
        self._load_monster(LEO_SPRITE)
        self.animator.animationFinished.connect(self._start_fly)
        self.animator.play(fps=SPRITE_FPS, loop=False)

    def _start_fly(self) -> None:
        self.phase = OverlayPhase.FLY
        self._disconnect(self.animator.animationFinished)
        self._load_monster(FLY_SPRITE)
        self.animator.play(fps=SPRITE_FPS, loop=True)

        self.fly_animation = QPropertyAnimation(self.animator, b"pos")
        self.fly_animation.setDuration(FLY_DURATION_MS)
        self.fly_animation.setStartValue(self.animator.pos())
        self.fly_animation.setEndValue(QPoint(self.width() + 200, self.animator.y()))
        self.fly_animation.setEasingCurve(QEasingCurve.Type.InQuad)
        self.fly_animation.finished.connect(self._finish_and_exit)
        self.fly_animation.start()

    def _cancel(self) -> None:
        self.status_message = "已取消，没有移动文件"
        print(self.status_message, flush=True)
        self._finish_and_exit()

    def request_exit(self) -> None:
        """Queue-safe exit entry point for terminal signals and UI actions."""
        self._finish_and_exit()

    def _finish_and_exit(self) -> None:
        if self._shutdown_started:
            return
        self._shutdown_started = True
        self.animator.stop()
        self.explosion_animator.stop()
        app = QApplication.instance()
        if app is not None:
            # Closing the last Cocoa window immediately can destroy QAudioOutput
            # while its worker thread is acquiring the Python GIL. Retire media
            # in the live Qt event loop first, then terminate in a second turn.
            app.setQuitOnLastWindowClosed(False)
        self.hide()

        players = [
            player
            for player in (self.bgm_player, self.sfx_player, self.explosion_player)
            if player is not None
        ]
        self.bgm_player = None
        self.sfx_player = None
        self.explosion_player = None
        self._retiring_players = players
        for player in players:
            player.stop()
            player.setParent(None)
            player.deleteLater()

        QTimer.singleShot(150, self._complete_exit)

    def _complete_exit(self) -> None:
        self._retiring_players.clear()
        self._shutdown_ready = True
        self.close()
        app = QApplication.instance()
        if app is not None:
            app.quit()

    def _auto_close(self) -> None:
        self._finish_and_exit()

    def closeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if not self._shutdown_ready:
            event.ignore()
            self._finish_and_exit()
            return
        self.animator.stop()
        self.explosion_animator.stop()
        super().closeEvent(event)
