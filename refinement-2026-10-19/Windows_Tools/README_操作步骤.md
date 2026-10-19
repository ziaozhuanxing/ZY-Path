# Windows：两项需要实际执行的检查

关闭 ZY-Path 后，在 PowerShell 中运行。代码使用项目现有虚拟环境，不修改分类默认缩放、应用逻辑或测试断言。

## 1. 修复训练脚本位置并运行完整 pytest

训练 ZIP 默认位置是你先前给出的 `E:\补全信息\dn21_folder_classification (1).zip`。
若它现在在别处，在命令末尾添加 `--training-archive "实际 ZIP 路径"`。

```powershell
& "E:\ZY-PATH\.venv\Scripts\python.exe" ".\run_windows_evidence.py" retest
```

工具仅提取真实 `train_crc_dn21.py`，校验 SHA-256，再复制到测试需要的
`models\dn21_folder_classification\train_crc_dn21 (1).py`。不同的已有文件会被保留并报错；不会覆盖。
模型文件也只检查和记录，不创建假模型。随后不筛选、不跳过测试，执行完整 pytest。

## 2. 用应用默认 Pillow 流程评估 7,180 张图片

你的 `E:\补全信息\CRC-VAL-HE-7K.zip\CRC-VAL-HE-7K` 是压缩包内部路径。
本工具读取实际 ZIP 文件，解压到同目录 `CRC-VAL-HE-7K-unpacked`，找到九类子文件夹后评估：

```powershell
& "E:\ZY-PATH\.venv\Scripts\python.exe" ".\run_windows_evidence.py" evaluate
```

需要两个原始 ZIP 都在上述位置，且项目中的分类模型与已验证的 epoch-26 权重一致。
实际调用项目 ModelLoader、Preprocessor 和 OutputParser，RGB/float32/raw255、224×224、Pillow bilinear、CPU、batch=1。
这测量 Single image 的核心计算，不验证 GUI 操作、Tiled analysis 或分割精度。

输出还包括：每张预测、每类指标、混淆矩阵、原图尺寸分布、与已安装 OpenCV 解码／缩放的输入张量差异，以及与旧预测 CSV 的标签一致数和最大概率差。
同为 224×224 的原生图片可能没有实际缩放差异；结果以运行输出为准。

## 输出与返回材料

两项各自在 `E:\ZY-PATH-evidence\retest-时间` 或 `evaluate-时间` 中生成记录。
第一项保存完整日志、XML、退出码、执行前后提交与状态、实际依赖和模型文件指纹。
第二项保存 summary.json、预测 CSV、混淆矩阵及环境／输入诊断；未完成时只留下 partial 预测文件，不生成完整成绩。

请将两个新证据文件夹打包后在聊天上传。原始数据图片和大权重无需再次上传。

没有在此工具中执行 Windows 原生测试；Linux 中的工具辅助逻辑测试与应用测试结果不能代替本机执行。
评估循环耗时包含诊断、CSV 和其他工作，不得当作正式分步骤推理性能。
