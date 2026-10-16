# Window lifecycle and theme follow-up to 7ec1556

This review covers the repair on `codex-ready-2026-10-15` against base commit
`7ec1556`. It supersedes the continuous screen-cap approach described in the
previous screen/grid review. Model loading, preprocessing, inference outputs,
tile coordinates, probabilities and statistics are unchanged.

## Causes and repairs

The previous implementation reapplied `setMaximumSize()` on resize, layout and
window-state events, and moved the native frame while maximized. These operations
interfere with the window manager's maximize/restore transaction and restore
rectangle. The window now leaves native flags and interactive sizing to Qt/the
window manager. Resize/move events log and record geometry without resizing or
changing state. The default Qt maximum size is retained, rather than installing
a screen-sized maximum. Native minimize/maximize/close flags are unchanged.

Available-screen correction is limited to startup, restored geometry, screen or
work-area changes and return to normal state. It uses logical
`QScreen.availableGeometry()` and includes decorations. Maximized, minimized and
fullscreen geometry is never adjusted by this correction. A short deferred
correction after first show/normal restore lets native decoration margins settle:
an X11 regression test caught the incorrect 0ms case, where maximized margins
were used while the window manager was restoring a normal frame. This is not a
resize/layout feedback loop. Fullscreen and maximized flags are logged separately;
legacy fullscreen state is cleared only during hidden startup restoration.

A further **reproduced native X11 issue** was found when closing a window
maximized from its native titlebar: Qt's `normalGeometry()` returned the current
maximized client rectangle, and `saveGeometry()` lost the smaller restore size.
The app now records the last stable normal client rectangle, separately from Qt's
packed geometry, as `window/normalGeometry`. It restores that rectangle before
startup maximization. Recording is debounced until normal state settles and
stops on managed state changes; it never applies geometry during interactive
resize. A valid distinct Qt restore rectangle is also retained on close. Legacy
settings without the extra rectangle still use Qt's packed geometry with bounds
correction. An already lost historical smaller rectangle cannot be reconstructed,
but normal resize is available and new normal sizes persist.

Scroll wrappers previously had surface backgrounds while their ordinary content
widgets inherited the application background. They now share an explicit themed
surface, with no extra frame. Property changes are repolished for already styled
containers. The input/action panels use 16px outer padding and 10px spacing; Run
Inference and Re-run retain this inset below the independently scrollable content.
Image viewing backgrounds and actual table borders remain intentional. Splitter
handles and scrolling are retained.

The classification tables were read-only but still selectable, with native
current/focus painting and no specific corner style. They now use enabled,
focusable `DisplayTable` widgets with NoSelection, NoEditTriggers and cleared
current/selection state on clicks, focus loss, tab changes, history load and
result replacement. A delegate suppresses focus/selection/hover fills and paints
the themed base or actual model color swatch before text. It does not blanket
override item backgrounds, which would hide the nine class colors. Arrow keys,
Page Up/Down and Home/End scroll the tables; Tab still moves focus.

Scrollbar tracks used native add-page/sub-page rendering, permitting stippled
page regions. Application-wide rules now define solid tracks, page regions,
corner, end buttons and handles in both orientations, with distinct hover,
pressed and disabled states. These rules cover panels, Settings, tables and
image views, without newly hiding scrollbars. Render tests sample all pixels in
interior page regions to check for solid fills, and exercise handle dragging.

## Evidence and limits

Artifacts: `/workspace/artifacts/window-theme-review/`.
The screenshots show **synthetic layout data**, not real model predictions.
No production checkpoint or user source image was available or fabricated.

Two validation environments are distinguished:

1. Qt **offscreen**: automated geometry/theme tests and synthetic small work areas,
   including 480×360, 640×480 and nonzero screen origin. High-DPI grid checks use
   125%, 150% and 200%. Grid transforms and classification invariants are checked
   by the existing tests.
2. Linux **Xorg dummy driver + Xfwm4**, Qt **xcb**, 1280×800 available area, DPR 1:
   real Linux window-manager decorations and state events. XTest clicks the native
   titlebar maximize/restore button and drags the bottom-right resize border.
   It is not an offscreen-only screenshot. It remains a Linux virtual display,
   not Windows-native validation or a hardware display test.

Native Linux sequence, repeated in Light and Dark themes:

| Action | Qt state | Client dimensions | Result |
|---|---:|---|---|
| Ordinary window | 0 | 960×680 | resizable native frame |
| Native maximize | 2 | 1280×776 | fullscreen false; native titlebar retained |
| Native restore | 0 | 960×680 | original dimensions restored |
| Native edge drag | 0 | 760×540 | smaller ordinary window |
| Native maximize → restore | 2 → 0 | 1280×776 → 760×540 | smaller dimensions restored |
| Minimize → restore | 1 → 0 | restored 760×540 | distinct from maximize |
| Explicit fullscreen → normal | 4 → 0 | 1280×800 → 760×540 | distinct from maximize |

`native-restart-states.json` additionally records the native close/restart case:
ordinary 760×540; native-maximized `normalGeometry` incorrectly 1280×776 while
`savedNormalGeometry` remains 760×540; restart maximized; native restore 760×540.
`native-restart.py` asserts the final size. `window-cycle.py` captures the repeated
native button/drag cycle and also checks maximized close/restart/restore.

Relevant evidence files:

- `after-native-normal-result.png`, `after-native-maximized-0.png`,
  `after-native-smaller-0.png`, `after-native-restored-1.png`.
- `dark-native-normal-result.png`, `dark-native-maximized-0.png`.
- `after-native-table-{1,2}.png`, `dark-native-table-{1,2}.png`,
  `after-native-settings.png`, `dark-native-settings.png`.
- `after-native-final-grid.png`, `after-native-grid-zoom-{in,out}.png`.
- `after-native-window-events.log`, `dark-native-window-events.log` and
  corresponding `*-window-states.json` include state/flags, client/frame,
  Qt normal rectangle, saved normal rectangle, available work area, DPR and limits.
- `related-tests.log`, `x11-tests.log`, `dpi-{1.25,1.5,2}.log`, `full-tests.log`.

Windows-native titlebar buttons, Windows decoration timing and mixed-DPI monitor
transitions **have not been verified** in this Linux environment. The app's INFO
logging now records the same state/geometry fields on Windows. To collect an
actual Windows run from the repository's PowerShell working directory:

```powershell
.\.venv\Scripts\python.exe main.py 2>&1 | Tee-Object -FilePath window-state.log
```

Repeat maximize → restore → resize smaller → maximize → restore, then close while
maximized and reopen/restore. Compare `normalGeometry`, `savedNormalGeometry`,
`maximized`, `fullscreen`, `frame` and `available` fields. This command is an
instruction for a Windows session, not a command verified in this Linux session.

## Final test results

| Check | Passed | Failed | Errors |
|---|---:|---:|---:|
| Related UI/classification/grid/history/Re-run/export tests, offscreen | 127 | 0 | 0 |
| New lifecycle/theme tests, X11/Xfwm xcb | 13 | 0 | 0 |
| Screen/grid tests at 125%, 150%, 200%, each | 7 | 0 | 0 |
| Complete pytest with collection errors retained | 237 | 1 | 1 |

The complete command is
`.venv/bin/python -m pytest -q --continue-on-collection-errors`.
Its remaining failure is
`test_default_builtin_paths_keep_real_classification_and_segmentation_models`,
because real built-in weights are absent. The collection error remains the absent
`models/dn21_folder_classification/train_crc_dn21 (1).py`, read by
`tests/test_train_crc_resume.py`. No tests are deleted/skipped or missing files
replaced by dummy weights/scripts. The known problems are not counted as passes.

The related command lists `tests/test_window_lifecycle_and_theme.py`,
`test_screen_fit_and_tile_grid.py`, `test_result_panel.py`,
`test_classification_modes_display.py`, `test_classification_tiles.py`,
`test_settings_dialog.py`, `test_ui_shell.py`, `test_inference_panel.py`,
`test_action_panel.py`, `test_history_panel.py`, `test_main_window_rerun.py`,
`test_main_window_export.py`, `test_main_window_delete.py`, all under `tests/`.
X11 runs just `tests/test_window_lifecycle_and_theme.py` with `QT_QPA_PLATFORM=xcb`;
DPI runs just `tests/test_screen_fit_and_tile_grid.py` with
`QT_ENABLE_HIGHDPI_SCALING=1` and the three `QT_SCALE_FACTOR` values.
`git diff --check` passes. Publication is recorded in the branch's Git history.

## Modified files

- `ui/main_window.py`: lifecycle correction, stable normal-size persistence, logs.
- `ui/theme.py`: panel surfaces, scrollbar states, table base and corner styling.
- New `ui/display_table.py`: display-only table behavior and painting.
- `ui/classification_result.py`: table integration and state cleanup.
- `ui/{inference_panel,action_panel,result_panel,history_panel,settings_dialog}.py`:
  borderless surfaces and panel spacing.
- `ui/zoomable_image_view.py`: themed widget surface only; grid/zoom math unchanged.
- New `tests/test_window_lifecycle_and_theme.py`: state ownership, saved ordinary
  rectangle, screen correction, table states, keyboard scrolling and rendered
  theme/scrollbar checks.
