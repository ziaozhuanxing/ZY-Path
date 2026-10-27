# CP2论文修订版 — Windows测试记录

正文保持英文。主文件为 LiZiYao_24018160_CP2_Thesis_Updated.docx，PDF为对应审阅版。

本版仅呈现实际提供的Windows测试记录：19 October 2026，源版本7bd3552，370 passed、0 failed、0 errors、0 skipped，15 warnings，194.10 s，exit 0。当前软件版本为8c4830c；上述较早结果不能作为后续变更的Windows通过记录。

正文与附录不再呈现其他平台的测试结果和覆盖率测量。最新发布资料包亦不含这些测试附件或会谈资料。软件源码、测试及依赖没有修改，没有执行新的软件测试。

保留的内容包括：当前界面功能说明、训练增强与加权细节、原图裁块与网络输入的区分、5张更新后的架构/UML图、需求追踪、UAT与性能协议、Windows验收表，以及原有真实分类评价。90.68% accuracy与88.59% macro-F1仍仅对应7,180张原生224×224 CRC测试patch。

32条参考文献、53处可点击引用、20张图及24张表保留；全部图表有明确正文提及。原有样式、图表来源和模型结果保留，目录与图表目录页码重新校核。

截图、UAT、封面信息和其他未提供的实测材料保持真实状态。评估表是尚未执行的方案，不是通过记录；开发界面示意图仍注明模拟或合成数据性质。

文件说明：
- Content_Changes.md / .csv：本版相对原Windows记录版本的修改位置、前后文本与原因。
- Citation_Locations.md / .csv：全部文献引用的位置。
- Figure_Table_Locations.md / .csv：全部图表的正文提及位置。
- Evaluation_Materials、UAT_Templates：未执行的任务协议、问卷和记录表。
- Windows_Tools：在实际Windows环境收集完整pytest证据的辅助脚本，尚未在本机执行。
- Evidence：Windows记录、分类评价及文档校核资料。
