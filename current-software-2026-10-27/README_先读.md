# 图表清理版 — 30 October 2026

- 重新绘制Figure 3.1、3.3、3.4、3.5、3.6，统一使用黑白节点和正交走线，分开箭头标签与连线，增加留白。
- Figure 3.2的原有界面线框图检查后保留。
- 类图按实际源码区分InferenceEngine → _OwnedWorkerThread → QThread与PdfExportWorker → QThread。
- 全部31个Word表格（24张编号表与7个证据占位框）统一使用Table Grid、白底、黑字、0.5磅黑色内外实线；删除彩色表头和交替底纹。文字、字号和表格尺寸保持。
- 已检查五张重绘图在PDF中的实际排版，图片及图注同页；更新目录、图表目录与引用位置。
- 新PDF共108页。32条参考文献、53处引用和所有正文图表提及保留；引用黑色、无下划线且保留既有点击目标。
- 正文文字、表格数据、模型评估结果和待补证据均未改写。
- 软件仍为3a935ef；已核验Windows测试仍为508 passed、0 failed、0 errors、0 skipped。本次不改软件、不重跑测试、不新增测试结论。

本次逐项变更见Content_Changes.md/csv；上轮文字审阅记录另存Editorial_Review_20261027_Changes.md/csv。图源SVG、印刷PNG、生成脚本及几何检查记录位于Figure_Builder。PDF图表排版检查位于Evidence/Figure_Table_Presentation_Checks.json。

直接使用本目录Word和PDF；无需重新执行软件测试。截图、UAT及封面信息继续等待真实材料。
