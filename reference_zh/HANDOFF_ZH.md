# GE2340 中文交接参考

本说明将 Alex（你）已完成的数据与基线工作，与 Jeffrey 需要完成的模型任务分开列出。内容对应组员使用的[英文交接说明](../docs/HANDOFF.md)，配合 v3 数据代码包和[英文分析报告 v5](../GE2340_Data_Analysis_EN_v5.md)使用。文件路径均相对于代码包根目录。

**Jeffrey 从 B 部分开始，查看自己的任务、输入文件和交付要求。** A 部分记录你已完成的工作，C 部分列出共享输入及标签定义。

## A 部分：Alex（你）已完成的工作与提供的材料

### 已完成的数据准备与基线

- 检查五项每日时间分配变量、缺失值、重复记录和学生 ID。全部 2,000 条记录均予以保留，无需填补。
- 使用随机种子 2340，固定划分为 1,200 条训练记录、400 条验证记录和 400 条测试记录，并保留稳定的行 ID。
- 标准化参数仅在训练集预测变量上拟合，再原样应用于验证集和测试集。
- 完成训练集分布、相关性、散点图和异常值标记，以及验证集预测和残差诊断。
- 完成 OLS 回归和训练均值基线，提供各数据子集的预测值及 MAE、RMSE、R²。
- 固定相对成绩标签并完成训练多数类基线，提供类别数量、预测值、混淆矩阵和分类指标。

### 已有回归方法

OLS 使用截距和四项未经标准化的时长变量，以体育活动为参照。五项时长之和为 24 小时，因此同时加入五项变量和截距会使各系数不唯一。总时长约束仍保留体育活动的信息。每个系数表示：保持其他已纳入模型的活动时长不变，将时间从体育活动转移到对应活动时，预测成绩的变化。

提交版 Phase 1 方案规定使用 MSE，与 OLS 的平方误差目标一致。等级边界和回归目标均已固定。来源核对记录见 [PHASE1_VERIFICATION.md](../docs/PHASE1_VERIFICATION.md)。

### 已有分类基线

多数类基线始终预测为 B。该类别根据训练集数量选出，占 1,200 条记录中的 249 条。验证集 Accuracy 为 15.50%，Macro-F1 为 0.05368；测试集 Accuracy 为 18.75%，Macro-F1 为 0.06316。完整精度结果保存在 CSV 中。

### 提供给报告和 slides 的材料

报告和 slides 撰写者从[英文 v5 报告](../GE2340_Data_Analysis_EN_v5.md)开始阅读，用 [FINDINGS.md](../docs/FINDINGS.md)查阅补充细节，并从 `outputs/figures/` 取用原图。报告中的图 3 对应 `04_validation_diagnostics`，`03_relationships_train` 则是补充散点图。

v5 报告和现有输出涵盖数据分析及基线结果。活动时长与成绩的关系应解释为关联。当前性能结果适用于本数据集及固定划分，跨学校的预测表现尚未检验。

### 复现你的结果

运行命令见 [README.md](../README.md#run-the-existing-pipeline)。包内包含原始数据压缩包和 CSV。已有结果可以直接打开查阅。

## B 部分：Jeffrey 需要完成的任务与交付内容

### 必做与选做模型

| 任务 | 预测目标与方法 | 评价与比较 |
|---|---|---|
| Softmax 分类器（必做） | 使用 SGD 和交叉熵损失训练，预测 A/B/C/D/F | 提供 Accuracy 和 Macro-F1，与已有多数类基线比较 |
| 小型神经网络（选做） | 预测原始单位下的连续 `Grades` | 提供 MAE、RMSE 和 R²，与已有 OLS 和训练均值基线比较 |

Jeffrey 的必做模型任务是 Softmax，小型神经网络作为选做扩展。当前数据包尚未包含这两个模型的结果。从下列已准备好的输入文件开始，复用 Alex 已完成的数据分析和基线结果。

### 使用哪些输入文件

以下路径均相对于代码包根目录。

| 文件 | 用途 |
|---|---|
| `outputs/processed/train_scaled.csv` | 训练用的五项标准化预测变量、原始 Grades 和 row_id |
| `outputs/processed/validation_scaled.csv` | 验证集输入和目标 |
| `outputs/processed/test_scaled.csv` | 测试集输入和目标 |
| `outputs/processed/split_manifest.csv` | 所有模型共用的固定样本划分 |
| `outputs/processed/preprocessor.json` | 在训练集上拟合的标准化参数 |
| `outputs/processed/grade_labels.csv` | 相对成绩标签，通过 row_id 一对一连接 |
| `config/grade_bands.json` | 固定阈值、类别顺序及边界规则 |
| `src/load_data.py` | 读取指定子集，返回行 ID、五项预测变量和连续 Grades |
| `outputs/metrics.csv` | OLS 与均值基线的回归指标 |
| `outputs/classification_metrics.csv` | 多数类基线的分类指标 |

### 遵循哪些实验设置

Softmax 预测固定成绩类别。若实现选做的神经网络，则预测原始单位下的连续 `Grades`。保留连续 `Grades` 和分类标签。按 `row_id` 连接标签，并保持特征行的顺序。

沿用现有数据划分和预处理参数。使用训练集和验证集选择超参数及停止训练的时点。测试集回归结果、类别数量和基线指标已经查看过。后续实验继续固定测试集划分和等级边界。

当前基线均用 1,200 条训练记录拟合。如果最终需要合并训练集与验证集重新拟合，各比较模型须采用统一方案。

### 需要交回什么

以下材料须为 Softmax 提供；若完成选做的神经网络，也为该模型提供相同材料。

- **代码：** 模型的可运行实现，以及复现实验的操作说明。代码整合可以与 Alex 共同完成。
- **方法与设置：** 说明已完成的模型、训练流程、选定的超参数，以及如何根据验证集选择这些设置。
- **实验结果：** 提供已完成模型的评价指标和比较表，使用上表对应的基线，并注明每项结果所属的数据子集。
- **图表与解释：** 提供实验图表，说明主要发现、模型差异和局限，供报告及 slides 使用。

将这些材料交给文书 A 撰写英文报告，交给文书 B 整理模型比较和 slides。文书 B 根据提供的结果、图表和解释制作展示材料。

回归比较使用 MAE、RMSE 和 R²，对比均值基线和 OLS；若完成选做实验，再加入神经网络。分类比较使用 Accuracy 和 Macro-F1，对比多数类基线与 Softmax。现有分类输出也包含平衡准确率。

## C 部分：共享参考——数据、特征与标签

包内的 Kaggle 版本 3 文件 `data/raw/student_lifestyle_dataset..csv` 包含 2,000 行、9 列。目标变量为 `Grades`，观测范围为 5.60 至 10.00，保留原始单位。来源及许可详见 [DATA_LICENSE.md](../DATA_LICENSE.md)。

共享特征顺序固定如下：

1. `Study_Hours_Per_Day`
2. `Extracurricular_Hours_Per_Day`
3. `Sleep_Hours_Per_Day`
4. `Social_Hours_Per_Day`
5. `Physical_Activity_Hours_Per_Day`

`Student_ID` 用于标识记录；`Gender` 和 `Stress_Level` 不作为模型输入。原始采集方法、总体代表性，以及数据来自真实观测还是合成生成，尚未核实。

等级边界由训练集五分位数计算并固定：

| 标签 | Grades 区间 |
|---|---|
| F | Grades < 7.10 |
| D | 7.10 ≤ Grades < 7.55 |
| C | 7.55 ≤ Grades < 8.00 |
| B | 8.00 ≤ Grades < 8.45 |
| A | Grades ≥ 8.45 |

处于边界的分数归入较高组。F 表示相对成绩最低的一组，不代表官方的不及格类别。类别顺序为 F、D、C、B、A，可编码为 0、1、2、3、4。同分记录归入同组，因此各类数量不完全相等。

## 附录：演示程序与网页（补充）

现有[本地模型演示页面](../app/demo/index.html)已接入 Alex 的线性回归。后续连接训练好的 Softmax 时，可以复用输入区和分类结果展示；接入方式见[模型接口说明](../app/demo/README.md#adding-jeffreys-softmax-classifier)。

展示时可查阅[应用说明](../app/README.md)，其中包含 Windows 程序、网页版及开发说明。完成模型实验后，可按展示需要选择是否将 Softmax 接入界面。
