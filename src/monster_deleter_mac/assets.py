from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


UPSTREAM_REPOSITORY = "https://github.com/531149627/MonsterDeleter"
UPSTREAM_COMMIT = "f2c43fd3c7efc6bb309d52d4f3884197fcaeaf40"

ASSET_ROOT = Path(__file__).resolve().parent / "assets"

SPRITE_COLUMNS = 5
SPRITE_ROWS = 3
SPRITE_FRAME_COUNT = SPRITE_COLUMNS * SPRITE_ROWS
SPRITE_FPS = 8
MONSTER_HEIGHT = 250
EXPLOSION_HEIGHT = 150
WALK_DURATION_MS = 4500
FLY_DURATION_MS = 2000
POINT_FRAME_INDICES = (11, 12, 13, 14)
KICK_EXPLOSION_FRAME = 5

WALK_SPRITE = "走路动效_spritesheet_transparent.png"
POINT_SPRITE = "指着文件_spritesheet_transparent.png"
KICK_SPRITE = "踹文件动效_spritesheet_transparent.png"
LEO_SPRITE = "雷欧登场_spritesheet_transparent.png"
FLY_SPRITE = "出场飞行动效_spritesheet_transparent.png"
EXPLOSION_SPRITE = "爆炸_spritesheet_transparent.png"
SELECTION_BACKGROUND = "选择界面/选择界面.png"
BGM_AUDIO = "音频/bgm(1).mp3"
VOICE_AUDIO = "音频/怪兽说话.mp3"
EXPLOSION_AUDIO = "音频/爆炸.MP4"


@dataclass(frozen=True, slots=True)
class UpstreamAsset:
    size: int
    sha256: str


# Exact byte identities from UPSTREAM_COMMIT. Tests protect against accidental
# replacement, recompression, or regenerated stand-in art.
UPSTREAM_ASSETS = {
    FLY_SPRITE: UpstreamAsset(
        701158, "6980243dc6adaafbeb9f233ee8ce0bba57eb429101351e3cebf4cbd398b996db"
    ),
    POINT_SPRITE: UpstreamAsset(
        1007058, "d5486d23dd2789a3aa2dd96939b1c4ce687751dba84d00afada9740e54fbc484"
    ),
    EXPLOSION_SPRITE: UpstreamAsset(
        13026141, "7536c15fafe01a1a38fd1553dd6da2aaa14d641a348da9b36e2699110c7eb97b"
    ),
    WALK_SPRITE: UpstreamAsset(
        1032445, "0059ec5fe34ead82a65fc6a7a485b0ec3f9ff5c5d65183d690946aae00ed43ce"
    ),
    KICK_SPRITE: UpstreamAsset(
        954792, "75857e721d01aebc2eaba3d7ede4d21bf6bf4e8c7a26175264654d50e84c1dca"
    ),
    LEO_SPRITE: UpstreamAsset(
        811625, "3e7ec9f4b13db6152a3ddd578cf04a7f2a1ba31dc0eb728b9dbce207ce0bd3ed"
    ),
    SELECTION_BACKGROUND: UpstreamAsset(
        1880572, "8cf6431a4b61841527c15fa2cadf0ea17e60b521e4d69af7e5dbf36460a52d92"
    ),
    BGM_AUDIO: UpstreamAsset(
        1985925, "c4342da1bd4739a0b61fa5501f0fef8c66216cdfabda25b9e3740123ea794c29"
    ),
    VOICE_AUDIO: UpstreamAsset(
        2304635, "a44348dc01e3c06affc70bb4dd1acbfdc9aee4d03e150bf2069e0352202b357e"
    ),
    EXPLOSION_AUDIO: UpstreamAsset(
        2446814, "91538594207ba458507359bdc54cb1558e5cfa14130be5930e1d33d7d9078610"
    ),
}


def asset_path(relative_path: str) -> Path:
    path = ASSET_ROOT.joinpath(*relative_path.split("/"))
    if not path.is_file():
        raise FileNotFoundError(f"缺少上游资源：{path}")
    return path
