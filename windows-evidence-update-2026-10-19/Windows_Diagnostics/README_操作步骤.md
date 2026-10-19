# Windows 诊断工具

默认Pillow的7180张评估已成功，无需重跑。

关闭ZY-Path后，以项目原虚拟环境运行本文件夹内的诊断脚本：

```powershell
& "E:\ZY-PATH\.venv\Scripts\python.exe" ".\diagnose_windows_tests.py"
```

脚本依次执行四组：历史双击测试、最小窗口布局测试、整个Re-run模块、完整pytest。各组在独立进程运行，前三组是诊断子集，不能与最后一组的数量相加。单组崩溃后仍会执行后面的组。

不会修改应用源码、测试文件或模型，不会跳过/弱化断言，不改变默认缩放，不强制offscreen/windows平台。原测试决定Qt环境，探针记录实际平台、窗口几何、最后执行项和即时失败详情；保留完整测试原有行为。

输出：E:\ZY-PATH-evidence\diagnose-时间。上传这个文件夹的ZIP即可；没有生成XML也照常上传。

Linux已验证工具在子进程骤停时仍保存先前断言，并能继续下一个进程；还在相关13项原测试上检查了探针。Windows实际诊断结果仍需要本机执行。
