# Windows 第二轮修复和复测

先退出 ZY-Path。无需管理员权限，不必换 Python/Qt，不必更改模型，不必重新执行 7,180 张分类评估。

此版本接受 1f3e01e 基线、此前宽度修复以及上一份 Windows_Regression_Fix 安装后的已知文件。安装前检查全部目标文件；不认识的改动会停止，避免覆盖其他修改。保留原始字节备份及原有 LF/CRLF 换行。重复运行安全。

```powershell
& "E:\ZY-PATH\.venv\Scripts\python.exe" (Join-Path $fix2 "apply_regression_fix.py")
if ($LASTEXITCODE -eq 0) {
    & "E:\ZY-PATH\.venv\Scripts\python.exe" (Join-Path $fix2 "verify_windows_fix.py")
}
```

验证器先执行 125 项相关测试，成功后执行完整套件；现有 362 项加本轮六项回调生命周期测试，完整套件应收集 368 项。只报告每次实际执行记录，不把两次通过数量相加。相关测试失败时停止，不会执行完整测试。

请将最后显示的 `E:\ZY-PATH-evidence\verify-fix-时间` 文件夹压缩上传。包括所有日志、XML、退出码、前后源码状态。若失败，新增的只读快照会记录实际 Qt 平台、原生边距和控件尺寸，供继续核对。没有逐行/鼠标事件跟踪；快照不改变测试断言。应用 INFO 日志单独保存为 application.log。

本轮重点：

- 修复窗口销毁后仍执行排队的模型校验 lambda：连接改为 Qt 管理的 QObject 绑定方法，覆盖内置模型、自定义模型和设置页。
- Tile details 移到分类结果顶部，避免小窗口大字体下横向溢出。
- 分割图例根据实际卡片高度保证至少一张完整卡片可以显示和滚动到。
- 推理面板保留 Run/Cancel 按钮的必要高度，同时保留之前的可读最小宽度。
- 最大化测试区分 Windows 的不可见原生调整边框与 offscreen 的合成 2px 边框。Windows 检查客户区位于可用区域，且 frameGeometry 与 Qt 的真实 frameMargins 一致；普通窗口与还原窗口仍检查完整边框包含关系。不更改应用最大化状态或窗口 flags 来迎合测试。

保留上一轮线程销毁保护、历史行高及结果滚动修复；没有删去测试，没有跳过测试，没有弱化模型断言。模型输出、默认 Pillow bilinear、分类比例、预处理和网格变换不变。软件分支尚未提交或推送。Windows 本轮结果须等实际执行后确认，Linux 结果不能替代 Windows 实机验证。
