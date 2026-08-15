# MonsterDeleterMac implementation plan

## Scope

Create an authorized macOS port of the public MonsterDeleter project using the exact upstream animation assets and timing. The project must run locally from an isolated Python environment, preserve safe Trash behavior, and integrate with Finder through a Quick Action.

## Acceptance criteria

- [x] A new project exists at `~/Desktop/MonsterDeleterMac`.
- [x] `uv sync --dev` creates an isolated environment with PyQt6 and send2trash.
- [x] `uv run monster-deleter-mac --demo` opens a transparent, always-on-top macOS overlay.
- [x] A selected target filename is displayed and requires explicit confirmation.
- [x] Confirming a real target sends only that file to Trash; cancel and Escape never delete anything.
- [x] Protected paths and directories are rejected before the overlay starts.
- [x] A Finder Quick Action installer and uninstaller are included.
- [x] Automated tests cover argument parsing, target safety, and trash behavior with a fake backend.
- [x] An offscreen smoke test proves that the Qt application can start and stop without deleting files.
- [x] README documents setup, usage, Finder integration, safety, and upstream inspiration.

## Implementation checklist

- [x] Add packaging metadata and dependency declarations.
- [x] Implement CLI and launch request validation.
- [x] Implement safe Trash service abstraction.
- [x] Port the original spritesheet player, confirmation UI, explosion, audio, and exit animation.
- [x] Implement Finder Quick Action templates and installers.
- [x] Add unit and smoke tests.
- [x] Install dependencies and run validation.

## Review

Implemented the authorized macOS port using the exact upstream character, explosion, selection-screen, and audio files from commit `f2c43fd3c7efc6bb309d52d4f3884197fcaeaf40`. Verified on macOS 15.4.1 with Python 3.13.11: the real Cocoa animation and audio sequence completes successfully, shell scripts parse, Python modules compile, and both generated Quick Action property lists pass `plutil -lint`.

No real user file was moved during verification. Trash behavior is covered with an injected fake backend, while demo and dry-run paths prove the UI flow remains non-destructive.

## Demo exit regression (2026-08-15)

- [x] Confirm the reported process is waiting in the Qt event loop rather than installing or crashing.
- [x] Stop the exact stale demo processes.
- [x] Print a clear terminal message explaining that the demo is waiting for UI confirmation.
- [x] Add responsive `SIGINT` and `SIGTERM` handling around the Qt event loop.
- [x] Add a subprocess regression test for terminal `Ctrl+C`.
- [x] Run the full test suite and verify the real CLI process exits on signal.

Review: `uv run pytest` passes all 16 tests. A real PTY run prints the startup guidance and exits cleanly with status 130 after `Ctrl+C`, without a traceback or residual process. The signal handler only requests event-loop shutdown, avoiding Qt widget destruction during active animation callbacks.

## Upstream animation fidelity (2026-08-15)

Scope: the user confirmed direct permission from the upstream author. Replace the clean-room placeholder monster with the original repository's character assets and animation sequence; do not invent replacement animation.

- [x] Audit the upstream asset tree and animation state machine.
- [x] Record the exact upstream revision used.
- [x] Package the authorized original frames with the Mac project.
- [x] Port frame timing, direction, targeting, attack, explosion, audio, and exit behavior to PyQt6/macOS.
- [x] Remove the placeholder QPainter monster implementation.
- [x] Add asset integrity and animation-sequence tests.
- [x] Update README attribution and permission note.
- [x] Run all automated checks and visually verify the real macOS animation.

Review: all 10 upstream resources match their recorded SHA-256 values, the package wheel contains the assets, and all 31 tests pass. A real macOS scripted demo completed the full selection → walk → point → confirm → kick/explosion → Leo → flight sequence in 12.86 seconds without moving a file. QtMultimedia uses a two-stage event-loop teardown to avoid the Cocoa/QAudioOutput/GIL deadlock; full animation, early cancel, and PTY `Ctrl+C` all exit cleanly with no residual process.

## Public GitHub release (2026-08-15)

- [x] Confirm generated files, environments, caches, and local scrape artifacts are ignored.
- [x] Scan the publishable tree for credentials and oversized files.
- [x] Run the automated test suite before publishing.
- [x] Initialize a `main` branch and create the initial commit.
- [ ] Create `Youhai020616/MonsterDeleterMac` as a public GitHub repository and push.
- [ ] Verify the remote visibility, branch, and clean working tree.
