# Windows 修复与复测

请先退出 ZY-Path。无需管理员权限，不必更改 Python、Qt 或模型，不必重跑 7,180 张分类评估。

本包针对基线 1f3e01e7866d1b1f78103d817214f7dbb1cc5a56，接受已安装的推理面板宽度修复。

1. 用项目虚拟环境 Python 运行 `apply_regression_fix.py`。它先校验所有目标文件，再备份原始字节，保持 LF/CRLF 换行；遇到不认识的改动就停止，避免覆盖个人修改。安装失败时回滚已写入文件。重复运行安全。
2. 用相同 Python 运行 `verify_windows_fix.py`。先运行相关测试，相关测试成功才运行完整 pytest；如失败或进程退出，保留实际结果并停止。
3. 把输出的 `E:\ZY-PATH-evidence\verify-fix-时间` 文件夹压缩上传。保留日志、XML、退出码和源码差异；不要只截取最后一行。

```powershell
& "E:\ZY-PATH\.venv\Scripts\python.exe" (Join-Path $fix "apply_regression_fix.py")
& "E:\ZY-PATH\.venv\Scripts\python.exe" (Join-Path $fix "verify_windows_fix.py")
```

修复范围：

- core/inference_engine.py：父对象强制销毁前，等待后台线程结束；正常窗口关闭仍使用已有的异步等待。覆盖模型验证、推理和设置中使用的同一验证线程。
- ui/history_panel.py：显示记录时完成行高计算；延迟列宽调整不再改变点击位置。字体和主题变化时仍更新行高。
- ui/inference_panel.py：保留已验证的外侧边距计算修复。
- ui/classification_result.py、ui/image_comparison.py：包含上一轮尚未在 Windows 安装的短页面/大字体滚动修复。
- tests/test_history_panel.py、tests/test_worker_lifetime.py：新增三项回归用例，保留全部原有测试和断言。

不会提交或推送软件分支，不改变预处理、Pillow 默认缩放、模型输出、分类比例或网格坐标变换。完整套件原有 359 项，加上本次三项为 362 项；不同调用的通过数不能相加。Windows 结果待这次执行后才能报告。

Linux 验证：相关 119 passed；字体 DPI 168 的历史及对照测试 24 passed；完整 361 passed / 1 failed / 0 collection errors，14 warnings，104.36s。唯一失败需要 Linux 安装中缺失的真实分割权重。安装工具另有 4 项检查通过，验证备份、换行、重复运行和未知改动保护；这些不是软件测试通过数。
