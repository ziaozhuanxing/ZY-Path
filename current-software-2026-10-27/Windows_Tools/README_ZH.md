# Windows 完整测试证据采集

此工具只采集当前源码与实际完整 pytest 的结果，不安装依赖、不复制或生成模型、不改动测试、不提交推送。请先关闭软件，并使用实际项目虚拟环境执行。

```powershell
& "E:\ZY-PATH\.venv\Scripts\python.exe" "下载目录\Collect_Windows_Evidence.py" --project "E:\ZY-PATH"
```

“下载目录”请替换为脚本真正所在的位置。默认证据写入项目旁的 ZY-PATH-evidence/thesis-时间戳目录，也可用 --output-root 指定其他新证据目录。

- summary.json 给出真实退出码和已生成的 JUnit 统计；若程序崩溃且没有完整 XML，不会编造通过总数。
- pytest-full.log 保留完整 stdout/stderr；command.json 保存实际命令。没有 --continue-on-collection-errors，也没有测试筛选。
- 保存测试前后的 HEAD、工作区状态与源码哈希。工作区不干净时会照实记录，不会替你还原文件。
- runtime-probe.log 是独立 Qt/PyTorch 环境探针，不能当作人工验收。若 Qt 平台被环境设置为 offscreen，就不能称为原生窗口验收。
- uv 虚拟环境没有 pip 时，依赖探针会保留失败记录，完整 pytest 仍照常执行；不要为了让探针成功而随意更改项目依赖。
- 运行需具备当前项目真实依赖、模型和测试前置文件。缺失时应修复真实资源或报告实际失败，不创建替代权重。
- 检查并脱敏后再分享整个证据目录。本工具不会联网上传证据。

本工具仅做了静态语法检查，尚未在你的 Windows 机器执行；没有预填任何新的 Windows 通过结果。
