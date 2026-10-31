# Windows人工验收怎么做



这份表只整理已经存在的证据，不代替你实际操作Windows。已有截图可复用。打开Windows_Manual_Acceptance_Reviewed.xlsx的Cases页，按中文步骤逐项操作，把真实结果写入最后几列。



当前8项有部分证据、7项尚无完整操作记录；这不是8项通过或7项失败。判定Pass要满足该项全部预期条件。执行日期与资料核对日期分别记录。



## W01 — Launch and restore previous geometry

启动软件；还原为普通窗口；检查Run Inference可见；关闭再启动，观察窗口恢复。

- 已有：No complete execution record supplied for this case.

- 还需：启动软件；还原为普通窗口；检查Run Inference可见；关闭再启动，观察窗口恢复。

- 现有证据：无完整记录



## W02 — Maximise, restore, shrink, maximise, restore

依次最大化→还原→拖动缩小→最大化→还原；记录各次能否正常操作。

- 已有：No complete execution record supplied for this case.

- 还需：依次最大化→还原→拖动缩小→最大化→还原；记录各次能否正常操作。

- 现有证据：无完整记录



## W03 — Dock narrow, inspect comparison, restore wide

打开原图对照；把窗口贴靠半屏；再恢复宽窗口；检查上下/左右布局自动切换与图像对齐。

- 已有：No complete execution record supplied for this case.

- 还需：打开原图对照；把窗口贴靠半屏；再恢复宽窗口；检查上下/左右布局自动切换与图像对齐。

- 现有证据：无完整记录



## W04 — Fit, 1:1, zoom and resize a 49-tile result

恢复49块结果；打开网格与编号；依次Fit、1:1、放大、缩小、调整窗口；查看第49块坐标。

- 已有：49 numbered512-pixel tiles and paired Fit views are visible.

- 还需：Record1:1/zoom/resize transitions and inspect tile49 actual edge coordinates; screenshots do not show the full sequence.

- 现有证据：F4.3(b).png; F4.3(c).png



## W05 — Click toggle labels, padding and indicators; use Tab/Space

分别点击勾选框、文字和内边距；按Tab/Space；每次应只切换一次，键盘焦点应可辨认。

- 已有：No complete execution record supplied for this case.

- 还需：分别点击勾选框、文字和内边距；按Tab/Space；每次应只切换一次，键盘焦点应可辨认。

- 现有证据：无完整记录



## W06 — Open both history calendars

打开History的两个日期日历；查看英文月份/星期；选择日期并核对筛选。

- 已有：No complete execution record supplied for this case.

- 还需：打开History的两个日期日历；查看英文月份/星期；选择日期并核对筛选。

- 现有证据：无完整记录



## W07 — Restore/rerun after changing current defaults

先记下历史记录数；恢复一条记录应不新增；改当前设置后对该记录Re-run，核对记录参数。

- 已有：History includes both modes; completed recorded Re-run83 retains512/49 while current defaults show256/196.

- 还需：Record before/after history count for restoration alone and confirm recorded model/task under changed current defaults.

- 现有证据：F4.5(a).png; F4_5_Rerun_completed_83.png; F4_5_Rerun_parameters_83.png



## W08 — Cancel a real workload and close while busy

启动真实分块工作后Cancel；核对历史无半成品；另一次运行中关闭窗口，记录清理与退出结果。

- 已有：Independent observations: classification progress228/400 withSession record79; separate cancellation acknowledgement withretained classification record78 andSegmentation selected. No continuous before/after sequence established.

- 还需：Record one continuous cancellation and history outcome; separately record close-while-busy cleanup. No transient Cancelling screenshot is required.

- 现有证据：F4.9(a).png; F4.9(c).png



## W09 — Scroll/maximise Settings at common display scales

记录实际显示缩放；打开Settings逐页滚到底并最大化/还原；检查内容、按钮和图例可访问。

- 已有：No complete execution record supplied for this case.

- 还需：记录实际显示缩放；打开Settings逐页滚到底并最大化/还原；检查内容、按钮和图例可访问。

- 现有证据：无完整记录



## W10 — Export, reopen PDF/PNG and inspect companion files

打开已导出PDF和PNG；核对同一记录的模型/任务/参数/统计；检查配套JSON和文件可读性。

- 已有：Actual two-page PDF opens; supplied JSON agrees with dimensions and all nine pixel counts. File listing showsPNG.

- 还需：Open the actualPNG and record its readability and identity. Only its listing was supplied.

- 现有证据：F4.6(a).png; F4.6(b).png; zypath_report_20261030_144310.pdf; zypath_result_20261030_144239.png.json



## W11 — Validate/save/restore defaults per task

Models分别保存/恢复每任务默认；用不相容任务的可信权重或不存在路径核对错误，不创建假模型文件。

- 已有：Test-model segmentation default is saved and built-in default restored; classifier default remains displayed.

- 还需：Check missing/incompatible-path messages and unchanged saved defaults. Test-model settings do not measure predictive accuracy.

- 现有证据：F4.9(d).png; F4.9(e).png



## W12 — Move required files and attempt restoration/rerun

只用真实文件的副本建立测试记录；临时重命名副本；尝试恢复/Re-run，应提示缺失且不静默换模型；再恢复副本名。

- 已有：No complete execution record supplied for this case.

- 还需：只用真实文件的副本建立测试记录；临时重命名副本；尝试恢复/Re-run，应提示缺失且不静默换模型；再恢复副本名。

- 现有证据：无完整记录



## W13 — Restore old tiles, edit preferences, Run; then use recorded Re-run

恢复旧512记录；将偏好改256后普通Run；再Recorded Re-run；最后再普通Run；分别核对512/256使用规则。

- 已有：Ordinary Run77 uses256/196; recorded Re-run83 uses512/49 despite current256/196 defaults.

- 还需：Complete and record the full old-record→changed-preference→Re-run→ordinary-Run sequence, including final new-run parameters.

- 现有证据：F4.5(d).png; F4_5_Rerun_completed_83.png; F4_5_Rerun_parameters_83.png



## W14 — Use tile numbers, image/table selection and Square; clear view/selection

点击编号与表格行，核对原裁块；Square后单独改高度；Clear view和Clear Selection后核对历史/文件仍保留。

- 已有：Number31 matches the crop preview, rectangle[1024,2048,1536,2560], NORM and59.47% confidence.

- 还需：Demonstrate Square copying once, independent width/height editing, Clear view and zero-row selection without removing saved data.

- 现有证据：F4.3(c).png



## W15 — Export both PDF qualities; cancel an export; reopen the output

同一结果导出两种PDF质量；核对数字一致；用专门临时文件测试取消覆盖，核对原文件未变。

- 已有：Standard PDF is875021bytes with quality/source dimensions and recorded numeric data.

- 还需：Compare both quality modes and numeric rows; cancel an overwrite of a disposable destination and check its prior hash is retained.

- 现有证据：zypath_report_20261030_144310.pdf; F4.6(b).png



## 完成后给我什么

把填写后的XLSX或CSV发回；如需新增证据，给对应截图/日志即可。不要先把空项批量改成Pass。无需重跑完整pytest。