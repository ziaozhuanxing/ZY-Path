# 狭小内容区的第三轮增量修复

请先退出 ZY-Path。此包以已安装的 Windows_Validation_Fix2 为前提，只更新两个文件：

- ui/action_panel.py：使右侧面板的滚动内容可在纵向收缩，避免原生滚动条的尺寸提示把整个三栏布局撑高。
- tests/test_screen_fit_and_tile_grid.py：新增两个回归用例，覆盖 16px 和 30px 滚动条、150px 内容区（30px 滚动条时 viewport 为120px）；检查两种分类模式、Run 与 Re-run 的完整可见范围，以及内部内容仍能滚动。

没有改旧测试断言、模型、预处理、默认 Pillow bilinear、结果、网格、窗口状态或屏幕适配逻辑。前两轮修复保持不变。

安装器先验证第二轮所需的全部前置文件，以及两个目标文件；未知改动即停止，避免覆盖其他修改。备份原始字节，保持 LF/CRLF 换行。重复运行安全。

```powershell
& "E:\ZY-PATH\.venv\Scripts\python.exe" (Join-Path $fix3 "apply_regression_fix.py")
if ($LASTEXITCODE -eq 0) {
    & "E:\ZY-PATH\.venv\Scripts\python.exe" (Join-Path $fix3 "verify_windows_fix.py")
}
```

验证器先执行131项相关测试（加入右侧面板原有4项测试及本次2项回归），全部通过后执行完整pytest。完整套件为370项：上轮368项再加本次2项。不同调用的通过数不能相加；相关测试失败时会停止，完整测试不会执行。

请上传最后显示的 `E:\ZY-PATH-evidence\verify-fix-时间` 文件夹 ZIP。保留日志、XML、退出码、源码状态和只读Qt快照。无需重跑7K分类评估，不需要管理员权限，也不需要修改Python、Qt或模型。

这次输入的Windows记录实际为124 passed / 1 failed / 0 errors，15 warnings，81.73s，完整测试未执行。Windows安装本包后的结果仍待实际运行，不能用Linux结果替代。软件分支没有提交或推送。
