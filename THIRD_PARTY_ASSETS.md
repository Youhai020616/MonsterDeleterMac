# Upstream assets and permission record

The character spritesheets, explosion spritesheet, selection image, and audio under `src/monster_deleter_mac/assets/` are exact copies from:

- Repository: <https://github.com/531149627/MonsterDeleter>
- Commit: `f2c43fd3c7efc6bb309d52d4f3884197fcaeaf40`
- Commit date: 2026-08-04

The user confirmed on 2026-08-15 that they had obtained the upstream author's permission to use these materials directly for this macOS port. No image-generation system or replacement artwork is used for the monster animation.

The port preserves the upstream 5×3 frame grids, selected pointing frames 11–14, 8 FPS playback, 4.5-second walk, kick-frame-5 explosion trigger, Leo sequence, 2-second flight, and original audio. Platform-specific changes are limited to macOS paths, Finder integration, process lifecycle, and the existing safe Trash validation.

Exact expected byte sizes and SHA-256 values are recorded in `src/monster_deleter_mac/assets.py` and verified by automated tests.
