"""MonsterDeleterMac package."""

import os


# Qt 6's FFmpeg backend otherwise dumps every media stream to Terminal. Keep
# actual decoder warnings visible while hiding verbose probe diagnostics.
os.environ.setdefault(
    "QT_LOGGING_RULES",
    "qt.multimedia.ffmpeg.*=false;qt.multimedia.ffmpeg=false",
)

__version__ = "0.2.0"
