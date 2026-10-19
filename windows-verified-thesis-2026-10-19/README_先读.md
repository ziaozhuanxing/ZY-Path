# CP2 Windows完整测试验证更新稿

这是正文内容修订稿，保留原Word样式及导师章节框架。Windows完整pytest已完成370项全部通过，旧中断记录仅保留为对应早期调用；本包没有需要再执行的诊断或补丁脚本。

- Word：LiZiYao_24018160_CP2_Thesis_Windows_Verified.docx
- PDF：同名审阅版，页数见Evidence/Document_and_Evidence_Checks.json
- 修改清单：Windows_Final_Changes.csv / .md（章节、修改前、修改后、原因）
- 待补材料：补图与待补证据清单.md；UAT_Templates；空白Windows_Manual_Acceptance_Record.csv
- Evidence/Windows_final_20261019：最终真实Windows日志、XML、退出码、源码记录，用户名和机器名已脱敏。
- Evidence/Earlier_records：早期结果保留供核对，不能当作当前结果。

这次只修改论文和资料，软件代码未修改、未提交、未推送。软件通过结果对应1f3e01e基线加已记录补丁，不能误称这些补丁已经是新提交。

分类默认Pillow评估保持90.68% accuracy、88.59% macro-F1（7180张原生224×224图块）；分块大图准确率和分割Dice/IoU不从自动化测试推定。UAT、七组真实截图、封面两项仍待补充；正式性能、分割来源/指标和干净机器打包保留其证据限制。
