# 中文参考资料

本目录供你个人查阅。组员从上级目录的英文 [README](../README.md) 接手。

## 中英文对照

| 内容 | 中文参考 | 英文主文档 |
|---|---|---|
| 分析报告 v5 | [中文 Markdown](GE2340_Data_Analysis_ZH_v5.md) | [英文 Markdown](../GE2340_Data_Analysis_EN_v5.md) |
| 技术交接说明 | [中文交接参考](HANDOFF_ZH.md) | [英文交接说明](../docs/HANDOFF.md) |

中文版报告按润色后的英文版逐段同步，章节、表格和引用相互对应。需要修改报告时使用 Markdown 文件。

## 文件与结果查询

- [中文文件索引](文件索引.md)：按用途查找数据、图表和实验输出。
- [英文技术结果说明](../docs/FINDINGS.md)：查阅详细指标、结果解释和图表对应关系。
- [英文接手入口](../README.md)：按组员任务选择阅读顺序，并查看运行命令。

## 当前 PDF

- [中文分析报告 v5 PDF](GE2340_Data_Analysis_ZH_v5.pdf)
- [英文分析报告 v5 PDF](../GE2340_Data_Analysis_EN_v5.pdf)

PDF 已按当前中英文 Markdown 分别重新生成。后续修改 Markdown 后，需同步更新对应 PDF。

## 演示程序与网页（补充）

### 网页

打开[演示页面](../app/demo/index.html)，输入每日时长后点击 Run prediction。页面默认将剩余时间分配给体育活动，也可取消勾选后手动输入五项时长。总时长须为 24 小时。

主结果显示相对分组名称及字母，例如 Middle group (C)，并显示取整后的“前百分比”，明确标注为训练集内的估计位置。参照为 1,200 条训练成绩，按高于预测值的数量加同分数量的一半计算；取整为零时显示“前 1% 以内”。连续预测值和均值基线可展开查看。页面使用英文，可离线运行；后续分类器的接入方式见[英文说明](../app/demo/README.md)。

### Windows 程序

[运行 GE2340 免安装版](../GE2340-Model-Explorer-1.0.0-Windows.exe)：内置模型，可离线使用；提供自定义标题栏和窗口按钮。源码与打包方法见 [app/desktop/README.md](../app/desktop/README.md)。
