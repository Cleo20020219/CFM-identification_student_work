# 学生交接验收（2026-10-31）

以下是此前在维护源码完成的学生交接验收记录，保留原有测试范围与计数。本发布副本把同一实现放在独立仓库根目录；复制核对与本次运行见[发布副本检查](PUBLISH_COPY_CHECK_ZH.md)。不要把历史全量测试计为本次重新执行；维护与发布关系见[同步规则](REPOSITORY_LAYOUT_ZH.md)。

## 已落实的交接内容

- 新应用统一从 `cfm_id.project` 进入，只读取 `cfm_id/configuration/reading.json`。旧默认与实验配置单列保留兼容，见[配置指南](BUSINESS_READING_CONFIG_ZH.md)。本轮没有修改 Prompt 文本。
- 现有五类 short_refs 事实家族共用组件登记：政策均值、两政策差值、局部效应、R3 观察性政策、变量 DAG。请求、解析、来源、格式诊断、条件交接和重读复用同一拥有者，专属目标和科学审核保持。
- `examples.student_handoff` 提供三个使用同一配置的完整教学示例。POINT 和 PARTIAL 均真实求解并独立重放；缺模型完整性条件时停在 NEEDS_INPUT，后端调用为零。
- 旧学生资料迁到 `examples/legacy`；历史配置与分轮状态记录分别进入 legacy / history。16个主目录和 Core / 适配器 / 文献的准确边界见代码地图。保留有回归用途的协议、原型和模型回答，不删除验证证据。

## 真正完成的测试

| 检查 | 最终结果 | 范围 |
|---|---|---|
| 固定框架 full | 2416 项通过，133 个子测试通过；执行期间源码不变 | 当前入口、五类读取、审核、恢复、兼容、POINT/PARTIAL 和证书 |
| 其余离线数学与兼容检查 | 2481 项通过，37904 个子测试通过；14 项跳过 | 与上一行文件集合不重叠；跳过是未分发的可选历史模型档案，不算通过 |
| 安装包内容 | 通过 | 无迁移前旧路径、缓存、密钥文件；wheel 中 Python 与当前源码一致 |
| 源码外隔离安装 | 22 项检查通过 | 新 venv，不继承 system-site-packages、不借用源码导入、不安装 Torch；pip check 通过 |
| 安装后的入口和 Mock | 12 个命令入口、Mock 7/7 通过 | 另完成创建会话、历史模型回答离线回放 |

两组源码回归合计覆盖 301 个测试文件。仅按现有离线脚本口径排除三个下游集成测试：`test_pipeline_smoke`、`test_identification_estimation_contract`、`test_minimal_pfn_diagnostic_ablation`；本轮未改 Estimation/Policy。其余离线测试没有因整理减少覆盖。

POINT 示例输出识别表达式和证书；PARTIAL 示例输出相对完整模型的 sharp `[3/7, 4/7]`；负例为 `BOUNDED_MODEL_DECLARATIONS_INCOMPLETE`。三者都使用固定教学草稿和显式合成审核，**不代表真实 LLM 准确率或真实企业科学批准**。

## 复现

从源码根目录执行：

```powershell
python -m pip install -e ".[test,documents]"
python -m examples.student_handoff --allow-synthetic-reviews --output outputs/student_examples
python scripts/check_framework.py --suite full --output outputs/framework_acceptance
python scripts/check_offline.py
```

测试需要系统允许本机 loopback HTTP 连接。构建时使用干净的 build / egg-info；不要在测试收集期间清理这些目录。完整安装验收还需将 wheel 安装进新 venv，在源码目录之外运行示例、Mock 和 CLI，并确认 import 路径为 site-packages。

本轮曾发现并修复 DAG 非法引用格式的旧错误码兼容差异；首次失败与后续通过记录分别保留。一轮因构建目录清理与测试收集并行而中断，没有计为通过。沙箱网络、临时目录权限和安装测试输出编码问题也保留原始记录，最终在合适的执行环境重跑；没有修改数学或放宽审核来消除失败。

机器可读摘要见 [HANDOFF_ACCEPTANCE.json](HANDOFF_ACCEPTANCE.json)。本机原始日志、JUnit、配置、三个完整输出、失败和重跑证据在 `LOCAL_EVIDENCE_NOT_DISTRIBUTED`，最终目录是 `framework_release`、`additional_verified`、`release_installed` 和 `release_wheel`。目录日期表示本轮启动日期，不表示每个运行的完成日期；历史明细不随源码包复制。

## 未解决的边界

业务首读仍不稳定，本轮按负责人决定暂不继续调 Prompt；独立来源、目标和科学审核继续保留。所有原生能力尚未从自然语言接通，有限 PARTIAL 不是任意模型求界器；IV、一般 ID、网络/DAG 联合模型和统一库外候选流程仍待扩展。Core 物理位置保留兼容，不宣称所有 Python 包已形成严格单向依赖。详见[完整限制清单](KNOWN_LIMITATIONS_ZH.md)。

本轮真实 API 调用 **0**；没有读取任何密钥。现有数学与 Prompt 实现未改；交接包是本地快照，不是另一个维护目录。
