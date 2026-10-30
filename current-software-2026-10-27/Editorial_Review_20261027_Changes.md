# CP2 editorial review — 27 October 2026



This edition follows the verified 508-pass Windows edition. Software source and test outcomes are unchanged.



## 1. 3.3.1

Before: Inference uses PyTorch on CPU. OpenVINO conversion is not implemented. The 27 October Windows resource manifest records 1,726,089 bytes (1.646 MiB) for the classification checkpoint and 489,488,187 bytes (466.812 MiB) for the segmentation checkpoint. Both files were present and unchanged through the test execution; Appendix E records their SHA-256 identities. These are stored checkpoint sizes. Structural compatibility permits supported model representations, not arbitrary task or label semantics.

After: Inference uses PyTorch on CPU. The 27 October Windows resource manifest records 1,726,089 bytes (1.646 MiB) for the classification checkpoint and 489,488,187 bytes (466.812 MiB) for the segmentation checkpoint. Both files were present and unchanged through the test execution; Appendix E records their SHA-256 identities. These are stored checkpoint sizes. Structural compatibility permits supported model representations, not arbitrary task or label semantics.

Reason: Remove an unexplained unimplemented technology from the method description; retain the actual PyTorch CPU runtime and genuine checkpoint sizes.



## 2. 3.6.6 / Table 3.6

Before: F16; N01–N08 groups; F17

After: F16; F17; N01–N08 groups

Reason: Keep functional requirements together, followed by non-functional requirements; preserve all evidence and status cells.



## 3. 3.3.4 → Appendix C.2

Before: The preference-lifetime regression defines a record at 8 × 7 source pixels, changes preferences to 16 × 12, restores or reruns the old record and starts a new run. For a 31 × 23 synthetic raster, its assertions require four real rectangles, including smaller right/bottom edges, while recorded rerun must retain its original geometry and backend. These small dimensions define deterministic test inputs and do not recommend a biological tile scale.

After: The unchanged synthetic crop-size example now follows the execution-history explanation in Appendix C.2.

Reason: Retain the precise test example while keeping the main methods focused on crop geometry and parameter precedence.



## 4. 3.4.2

Before: Tile boundaries and optional one-based tile numbers are drawn in source coordinates. Selecting a tile in an image or its detail row locates the same numbered crop and displays its original pixels, rectangle, label and confidence. The Square action copies the current width to the height once; dimensions remain independently editable. Numeric preference controls route wheel input to page scrolling. The expandable resize guide explains the available backends without changing the model or network input size.

After: Tile boundaries and optional one-based numbers share image coordinates. Selecting a tile or its detail row identifies the same source crop, rectangle, label and confidence. This supports spatial inspection without requiring a separate page for each result component.

Reason: Retain the interaction purpose; remove micro-level settings details already covered by the settings section and regression evidence.



## 5. 3.4.2

Before: In comparison mode, linked views share zoom and source-coordinate centres. Both panes use a common Fit scale rather than independently fitting dissimilar viewport widths. Narrow pages stack the pair vertically; widening restores horizontal comparison. When segmentation comparison is active, its legend stays below the images to avoid a wide-window side legend shrinking the comparison back below its horizontal-layout threshold.

After: Linked comparison uses a common Fit scale and source-coordinate centre for the original and result. The pair stacks vertically in narrow windows and returns to a horizontal layout when space permits. Panning, zooming and divider resizing preserve spatial correspondence without changing predictions or statistics.

Reason: Consolidate comparison design into its spatial guarantees instead of implementation-specific input handling.



## 6. 3.4.2

Before: Linked panning updates the peer view without repeatedly recentering the actively dragged pane. Resizing retains the intended source-coordinate centre, and divider dragging uses a rubber-band preview before the panes resize on release. Fractional wheel deltas produce proportional zoom while zero or horizontal-only deltas do not trigger an unintended zoom. These operations affect presentation and leave analysis values unchanged.

After: Consolidated into the preceding comparison paragraph; the implemented navigation remains unchanged.

Reason: Remove rubber-band and fractional-wheel implementation detail from the main design narrative.



## 7. 3.4.2

Before: The classifier grid is painted after the image with the same scene-to-viewport transform and an approximately constant logical line width. This avoids losing lines by pre-rendering a fine grid into a large image and then shrinking it. Fit, 1:1, manual zoom, resize and history restoration preserve source-coordinate alignment. The displayed scale accounts for device pixel ratio: 1:1 denotes one source pixel per physical display pixel, while window bounds are handled in Qt logical coordinates.

After: The classification grid is drawn over the image through the same coordinate transform, with a line width that remains legible during Fit and zoom. Image/grid alignment is preserved after resize and history restoration. The scale display accounts for device pixel ratio: 1:1 represents one source pixel per physical display pixel, while window bounds use Qt logical coordinates.

Reason: Keep the substantive coordinate and high-DPI design while reducing low-level rendering detail.



## 8. 3.4.3

Before: Result toggles use a padded rounded surface. Their complete visible area—including label and padding—accepts a mouse click. Mouse focus does not leave the former thick blue frame; keyboard Tab/Backtab focus retains a thin accent border, and Space toggles the state. Constant border width prevents focus/checked states from changing the control's size.

After: Result controls provide a consistent clickable area and visible keyboard focus. Mouse, keyboard and scrolling interactions are designed to prevent unintended parameter changes while keeping essential actions accessible.

Reason: Replace border-width and focus-paint detail with the user-facing accessibility principle.



## 9. 3.4.3

Before: Settings is resizable and scrollable. Preferences groups export reminders, classification mode, source tile dimensions, resize backend, separate colour references and layout reset. Selecting a mode applies to the main panel and startup default, while history restoration does not rewrite that default. Closed dropdowns pass wheel gestures to page scrolling rather than changing the selection accidentally.

After: Settings provides a resizable, scrollable interface for export reminders, classification mode, tile dimensions, resize backend, task-specific colour references and layout reset. Changes apply to the main panel and new-run defaults without rewriting stored analyses. The Square action copies tile width to height, while the resize guide explains backend choices.

Reason: Describe configuration behaviour and useful controls once; omit repeated wheel-event mechanics.



## 10. 3.4.3

Before: Guide & Support provides numbered guidance, persistent Contents navigation, previous/next actions and a reading-aware indicator. System Information displays runtime and dependency information before copying it, with confirmation expiring after 2.5 seconds. About reports version 1.0. Together these controls make configuration and support information discoverable within the application.

After: Guide & Support presents structured workflow guidance and reading-aware navigation. System Information displays runtime and dependency details that can be copied for support; About identifies version 1.0 and contact information.

Reason: Remove timing and navigation-button minutiae while retaining the support functions.



## 11. 4.3.1

Before: Earlier Windows iterations exposed missing training prerequisites, thread-lifetime faults, settings leakage and platform-dependent layout/path assumptions. Corrections addressed these causes while preserving production preference persistence and the behavioural assertions. The completed 508-case invocation includes the corrected cases. Table 4.5 summarises the resolutions; Appendix C preserves the earlier Windows outcomes.

After: Earlier Windows executions encountered a missing training script and thread-lifetime faults. The subsequent 8c4830c invocation reached execution but reported 17 failures and three teardown errors, attributable to settings leakage, compact layouts and platform-dependent path handling. Revision 3a935ef corrected these issues and completed all 508 cases. Table 4.5 summarises the resolutions; Appendix C distinguishes the executions and identifies the source changes.

Reason: Do not conflate earlier collection/crash faults with the causes of the 17 failures in the immediately preceding invocation.



## 12. 4.3.2

Before: The corrected cases retain their original behavioural checks; the suite additionally includes eleven lifecycle and viewport regression cases introduced during refinement. The Windows maximisation check uses the client area and Qt’s actual native frame margins, while normal/restored full-frame containment remains required. Classification performance is reported separately in Section 4.2.6.

After: The corrections preserve the required behaviours. Test-only QSettings isolation removes dependence on saved user preferences without changing production storage. The PDF path check still requires the complete recorded path, allowing only extracted carriage-return and line-feed layout characters, and adds a Windows-path case. No test was deleted or skipped. Appendix C identifies the saved before/after diff; classification performance is reported separately in Section 4.2.6.

Reason: State exactly how assertions changed and why; distinguish equivalent content checks from an unsupported claim that test expressions were untouched.



## 13. Appendix C.2

Before: No per-cause count or retained diff identified in the narrative.

After: The 17 failures at 8c4830c comprised seven settings-leakage cases, three default-window cases affected by saved maximised state, four large-font layout cases, one compact action-panel case, one PDF path-wrapping case and one portable build-path case. The three teardown errors accompanied failing settings-related cases and are not additional test identities. The 8c4830c-to-3a935ef diff is retained with the supporting materials as Windows_Regression_Fix.diff and Tests_Before_After.diff. The isolation fixture redirects default organisation/application settings only during pytest, retains explicitly file-based settings and verifies persistence within each isolated store.

Reason: Provide an accurate reproducible account of the 17 failures and the scope of test isolation for examination.



## 14. 4.3.1 / Table 4.4 caption

Before: Table 4.4. Windows host hardware record and verified test runtime.

After: Table 4.4. Windows hardware record (19 October) and test runtime (27 October).

Reason: Make the two collection dates immediately visible instead of implying a single contemporaneous hardware probe.



## 15. 4.3.1 / Table 4.4 source

Before: Source: host hardware recorded on 19 October 2026 and runtime/dependency records from the completed 27 October invocation. Physical RAM and GPU specifications were not remeasured in the later collection; the runtime probe confirms PyTorch CPU execution.

After: Source: hardware recorded on 19 October 2026 and runtime/dependency records from the completed 27 October invocation. The later collection did not remeasure physical RAM or GPU specifications; its runtime probe directly confirms CPU execution. The records are distinguished by date, and their same-device identity awaits confirmation.

Reason: Do not infer that two collections came from the same physical computer without confirmation.

