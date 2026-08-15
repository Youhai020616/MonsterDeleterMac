# Lessons

- Keep destructive behavior behind explicit confirmation and an injectable Trash service.
- If upstream permission is unclear, ask about authorization and expected visual fidelity before choosing placeholder art.
- Prefer a Finder Quick Action for a personal macOS utility; it is simpler and safer than a Finder Sync extension.
- Do not reject all of `/private`: macOS stores ordinary per-user temporary files under `/private/var/folders`. Protect only known critical subtrees.
- A Qt offscreen smoke test needs to quit the application event loop explicitly after closing the last test window.
- A GUI command launched from Terminal must print its waiting state and explicitly bridge `SIGINT`/`SIGTERM` into the Qt event loop; a visible window alone is not enough feedback.
- A Python signal handler must not destroy a Qt widget because it can interrupt that widget's active callback. Request event-loop shutdown and let process teardown release the UI safely.
- On macOS, do not call `QApplication.quit()` while QtMultimedia children are being destroyed from a Python callback. Retire `QMediaPlayer` objects with `deleteLater()` in the live event loop, then quit in a later turn to avoid a Cocoa/QAudioOutput/GIL deadlock.
- When the user asks for a port of an existing visual project, confirm whether they expect exact authorized upstream assets before substituting clean-room placeholder art. Do not present invented animation as fidelity to the original.
