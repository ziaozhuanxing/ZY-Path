# 一处布局修复与 Windows 原生平台验证

本次只修正 ui/inference_panel.py 的最小宽度：计入原有外层左右各16px的内边距。没有修改测试、模型、默认预处理、预测或分类统计。不会提交或推送软件分支。

apply_window_width_fix.py 会验证原文件的SHA-256（兼容LF/CRLF），先在 E:\ZY-PATH-evidence\window-width-fix-时间 下备份原文件，再应用已公开的两行计算改动；保留原行尾。遇到不同的本地修改会停止，重复执行已修复版本不再改文件。

关闭ZY-Path后，以项目Python运行：

```powershell
& "E:\ZY-PATH\.venv\Scripts\python.exe" ".\apply_window_width_fix.py"
```

成功后再验证：

```powershell
& "E:\ZY-PATH\.venv\Scripts\python.exe" ".\diagnose_windows_tests.py" --qt-platform windows
```

参数只在这个取证进程及其子进程中明确使用Windows原生Qt平台，不修改系统变量。原测试内的setdefault("QT_QPA_PLATFORM", "offscreen")会保留显式平台设置；测试和断言均保持原样。先运行三组诊断子集，再运行完整、不筛选的pytest；各组分别记录结果，不能把子集数量加到完整测试数量中。

实际平台由日志中的platform_plugin字段确认，不以Python的win32标签代替。先前原生Windows历史双击单项通过，offscreen下同一项失败；Re-run异常目前只取得offscreen记录，不能因此认定其根本原因或已经解决。仍需这次实际结果。

上传新生成的 E:\ZY-PATH-evidence\diagnose-时间 文件夹ZIP。无需重新评估7180张图片。

应用补丁后，git status显示 M ui/inference_panel.py 是预期情况，HEAD仍是原提交。诊断工具会记录运行前后状态；后续论文应标识“基线提交+宽度补丁”，不能把它写成未改动的旧版本测试。
