# Windows 精确崩溃取证

请使用当前已经应用宽度补丁的版本，关闭ZY-Path后运行：

```powershell
& "E:\ZY-PATH\.venv\Scripts\python.exe" ".\trace_windows_crash.py"
```

本工具不应用新补丁，不改源码、模型、原测试或断言，也不安装依赖或修改Windows注册表。

依次运行：
1. 单独运行固定崩溃的“缺失自定义模型后Re-run”用例。
2. 运行原Re-run模块，比较是否依赖前序测试。
3. 运行历史测试的原先前序模块和历史模块，捕获双击坐标与实际表格索引。

只在两个目标用例内启用项目源码行、pathlib/QtBot原生调用和Qt消息记录。若Qt发出致命消息，立即保存消息和Python线程堆栈；子进程崩溃后只读查询该进程PID对应的Windows Application Error事件。未取得事件不等于没有崩溃。

输出：E:\ZY-PATH-evidence\crash-trace-时间。请上传整个目录ZIP，尤其是execution-trace.jsonl、fatal-python-stack.log（若有）及windows-application-events.json（若有）。不需要重跑7K评估。

本次只做诊断子集，不运行完整359项，也不把跟踪模式的结果当作最终验收或计时。跟踪本身可能改变时序；原测试断言均保留，正式复测应在根因处理后不带逐行跟踪执行。
