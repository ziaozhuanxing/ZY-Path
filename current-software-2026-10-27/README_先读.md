# 论文证据与评估材料整理 — 30 October 2026

本次24项修改见Content_Changes.md/csv，按章节列出修改前、修改后和原因。正文保持英文，既有文档样式、彩色示意图、黑白实线表格与全部原截图保持。

## 已修正

- 已确认大图与导师分割模型训练数据都来自乳腺癌数据集；具体数据集名、MPP和分割Dice/IoU仍未知，不猜填。
- 分类模型训练于CRC数据。乳腺大图仅作软件流程演示，不能套用CRC外部测试90.68%的结论。
- 删除“还缺真实分割演示”的过时说法，真实截图和PDF/JSON已存在；缺少的是标注对照的定量评价。
- 已确认19日硬件与27日测试来自同一台Windows电脑，保留两个采集日期，不声称27日重测硬件。
- 去掉正文中反复要求截图提交号的说明；保留实际记录编号，不给截图猜填软件版本。

## Windows人工验收：不是再运行pytest

打开Evaluation_Materials/Windows_Manual_Acceptance_Reviewed.xlsx。Cases页有15项中文操作、原验收标准、已观察证据和剩余动作，最后几列留给你实际操作后填写。

当前8项有部分证据，7项尚无完整操作记录；不是8项Pass或7项Fail，没有新增虚构的执行结果。主要截图无需重复拍，Cancelling瞬间也不用反复截取。中文说明见Evaluation_Materials/Windows_人工验收操作指南.md。

## UAT：材料齐备，真实响应尚未收集

- UAT_Templates/ZY_Path_UAT_Questionnaire.docx：问卷。
- UAT_Task_Protocol.csv与论文附录B：任务脚本。
- UAT_Templates/ZY_Path_UAT_Data_and_Scoring.xlsx：真实响应空表，旧基线说明已更正；参与者、原始答题和任务结果未填写。
- UAT_Templates/SUS_Scoring_Checks_SYNTHETIC.xlsx：独立的合成算例，只检查公式；没有参与者、反馈或研究结论，不能作为UAT结果提交。
- Evaluation_Materials/UAT_Material_Register.csv：已登记真实224像素CRC例图、分类权重身份和分割结果；参与研究的许可、材料准备和本地可用性仍需确认。

已用独立计算与LibreOffice重算核对6组合成算例，并在真实响应模板的临时副本检查10种输入条件；全部符合预期。临时副本未混入真实响应空表或论文结果。

## 核对结果

PDF共117页；32条参考文献、53处黑色无下划线引用链接、20张图和24张表的正文提及均已核对；172个页码目标已刷新。七组实际图片和图注同页；无空白正文页或越界内容。原有24张表均为黑白实线表格。

仍留20处UAT待填字段和封面2处待确认；没有把尚未收集的响应、未执行的人工验收、性能或部署记录写成已完成。

软件代码和测试没有修改，也未重跑pytest。原有3a935ef的Windows完整测试508 passed、0 failed、0 errors、0 skipped记录保持不变，不混入Linux结果。
