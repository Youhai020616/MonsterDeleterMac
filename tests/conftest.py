import os


# All in-process Qt tests are non-interactive and must never cover the desktop.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
