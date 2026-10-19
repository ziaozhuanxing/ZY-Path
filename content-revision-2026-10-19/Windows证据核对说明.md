# Windows 原始证据核对说明

已收到并读取十个原始文件：dependencies.txt、commit.txt、hardware.txt、pytest.xml、pytest-exit-code.txt、pytest-full.log、python-version.txt、test-date.txt、runtime-device.txt、windows-app.log。

- commit.txt 为 1f3e01e7866d1b1f78103d817214f7dbb1cc5a56。
- test-date.txt 为 2026-10-19T14:21:40.3674502+08:00；JUnit timestamp 同为当地 +08:00 时间。
- pytest-full.log：win32；356 items collected / 1 error；13 warnings, 1 error in 24.76s；collection interrupted。
- pytest.xml：errors=1、failures=0、skipped=0、tests=1、time=24.755；其中 tests=1 是收集错误条目，不是通过测试。
- pytest-exit-code.txt 为 2。没有本次 --continue-on-collection-errors 执行记录或有效通过数量。
- 当前错误是缺少 models/dn21_folder_classification/train_crc_dn21 (1).py；未将旧模型缺失失败计入本次。
- runtime-device.txt：torch 2.1.2+cpu，CUDA False，24 CPU threads，GPU Not used。
- windows-app.log 中可解析 11 条 Window geometry JSON，记录普通、最大化和最小化状态；所有这些条目的 fullscreen 均为 false。
- 分类 checkpoint 加载完成，DenseNet / classification / classes=9 / output=(1,9) 校验成功，主窗口接受结果。
- 当前应用日志没有完成图像推理的记录，不据此判定模型精度、分块或分割功能已正式验收。
- git-status.txt 未在本次材料中出现；干净工作区是作者说明的后补检查，没有与之配套的后补 HEAD 输出。两者不合并成测试当时工作区／提交已双重核实。
- 硬件文件 RAM_GB=15.81 的 GiB 单位依据作者提供的采集计算说明（2^30）；单靠文件字段名不能重新核验计算过程。

共享副本仅去除 Windows 用户名和主机名，并转换为 UTF-8；测试状态、数值和项目相对路径保留。原始上传文件保持不变。原始与共享副本校验和均见 Evidence/Windows_20261019_redacted/Redaction_and_Checksums.json。
