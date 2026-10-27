# 固定版本的Windows完整测试

目标应用提交：3a935efaae05bf6cf15eda32d1c6e6aff2cc29d5。该提交已于27 October 2026完成Windows原生Qt完整测试：508通过，无失败/错误/跳过。无需为了本轮论文更新再次运行；以下命令仅供以后复现。

先关闭ZY-Path。测试期间不要更改源码、依赖或模型文件。请在实际Windows PowerShell中执行：

```powershell
cd E:\ZY-PATH
$tools = Join-Path $env:TEMP "ZYPath-CP2-Windows-Validation-20261027"
New-Item -ItemType Directory -Force -Path $tools | Out-Null
$script = Join-Path $tools "Collect_Windows_Evidence.py"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ziaozhuanxing/ZY-Path/cp2-thesis-2026-10-17/current-software-2026-10-27/Windows_Tools/Collect_Windows_Evidence.py" -OutFile $script
& .\.venv\Scripts\python.exe -B $script --project "E:\ZY-PATH" --expected-commit "3a935efaae05bf6cf15eda32d1c6e6aff2cc29d5" --require-clean-source --native-windows
```

本工具不自动更新或还原代码，不安装依赖，不复制/生成权重，不删除/跳过/筛选测试，也不推送软件。

## 运行前检查

- 必须是目标提交，工作区必须干净；不满足时在运行pytest之前停止。请保留现有改动并检查git status，不要直接reset。
- --native-windows明确让子进程使用QT_QPA_PLATFORM=windows；独立最小Qt探针失败时不会启动pytest。这个探针不是人工窗口验收。
- 需要真实的两项内置模型及测试读取的训练脚本。资源不存在时只如实记录，完整pytest仍会反映相应失败/错误，不创建替代文件。
- 三个资源路径：models/crc_dn21_seed42_best.pth；models/UPerNet_TME_tissue-panoptils_best_model_100ep.pth；models/dn21_folder_classification/train_crc_dn21 (1).py。

## 运行结果

默认证据目录：项目旁的ZY-PATH-evidence/thesis-时间戳。工具会显示实际目录。

- pytest-full.log、pytest.xml、pytest-exit-code.txt：完整测试与真实退出码；没有完整XML时不编造通过数。
- command.json、environment.json、runtime-probe.log：命令、环境、原生Qt平台探针。
- source-before.json、source-after.json：提交、工作区、源码哈希，以及真实资源的大小/校验和。
- summary.json：实际统计、源码/资源是否变化、平台探针结果及采集器退出码。源码或资源变化会使版本匹配检查失败，即使pytest本身返回0也不当作有效的固定版本记录。

执行后请将整个新证据目录压缩，检查个人路径后上传附件。云端无法直接读取E盘。收到日志后，再按实际结果同步摘要、表3.6、表4.3、表C.2、目标评估和第5章；若新运行通过，早期基线可移至附录并按实际日期/版本标识。

完整pytest与真实图片人工验收是不同环节；后者按Windows_Manual_Acceptance_Cases.csv记录。本工具已用于本轮实际Windows执行。日志、XML和退出码已经核对；自动化测试通过不预填人工验收结果。
