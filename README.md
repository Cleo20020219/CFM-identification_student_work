# Causal-IDFM · Identification

从业务问题和材料，到经审核的因果识别结果。LLM 提出读取草稿；研究者确认目标、可用总体信息和科学条件；数学模块检查适用域、应用定理并独立重放证书。用户不需要先选择数学方法。

```text
业务材料 → A0 草稿 → 业务意图与来源审核 → 专门事实读取
                                              ↓
逐问和整题结果 ← 独立证书重放 ← 数学执行 ← A4 信息 / A5 条件审核
```

读错后显式复查；缺条件时追问；方法未覆盖时报告覆盖缺口。未验证的 LLM 候选不能替代正式结论。当前是**需要审核的研究框架**，业务首读准确率仍有不足。

## 仓库与起点

这是独立的 [CFM-identification](https://github.com/zzyyLOGIC/CFM-identification) 仓库。clone 后直接在仓库根目录安装、运行和开发，无需进入 `research/identification/causal_idfm/` 子目录。负责人仍在原团队工作区维护，再将经过核对的代码同步到这里；详见[仓库布局与同步规则](docs/REPOSITORY_LAYOUT_ZH.md)。旧 ProjectCode 和原交接包不是开发起点。证书内部摘要保留，用于检查材料和审核的一致性。

新应用统一使用 [`cfm_id.project`](cfm_id/project.py)，读取唯一推荐配置 [`cfm_id/configuration/reading.json`](cfm_id/configuration/reading.json)。这是从已有合同中选定的教学起点，没有修改 Prompt，也不声称它的准确率最优。旧默认值和旧协议只为兼容保留，见[配置指南](docs/BUSINESS_READING_CONFIG_ZH.md)。

## 安装，运行三个完整示例

Python 3.11 或更新版本。在本目录执行：

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m cfm_id.project config
.venv\Scripts\python -m examples.student_handoff --allow-synthetic-reviews --output outputs/first_run
```

Linux/macOS 将 `.venv\Scripts\python` 换成 `.venv/bin/python`。输出目录必须是新目录。以上**不联网调用模型、不需要 API Key、不需要 Torch**。

| 示例 | 业务目标与条件 | 实际输出 |
|---|---|---|
| `point` | 服务网点采用同一 AI 安排时的平均结果；已声明完整总体信息和所需科学条件 | `POINT`，识别表达式、证书、独立重放 |
| `partial` | 合作网络中一个固定推广方案的平均结果；有限总体均值和完整有界模型 | `PARTIAL`，相对该模型的 sharp 界 `[3/7, 4/7]`，证书、独立重放 |
| `missing_condition` | 与 PARTIAL 同类目标，但模型完整性条件未确认 | `NEEDS_INPUT`，列明缺项，不调用求解器 |

每个目录保存业务原文、两次读取请求与固定草稿、合成审核、计划、逐问结果及整题结果。**草稿是教学夹具，审核是显式合成审核，不是实时 LLM 结果或真实企业批准。** 源码见 [`examples/student_handoff.py`](examples/student_handoff.py)。

真实业务创建会话：

```python
from cfm_id import project
from cfm_id.business_intake import prepare_request
session = project.start(case)   # case 是含问题和材料的 BusinessCase / dict
request = prepare_request(session)  # 只准备请求；不调用模型、不自动审核
```

也可执行 `python -m cfm_id.project start --input case.json --output outputs/new_case`。后续接收回答、逐项审核、分派与执行见[会话操作](docs/BUSINESS_INTAKE_ZH.md)和[业务分派](docs/BUSINESS_DISPATCH_ZH.md)。

## 开发阅读顺序

分类的综述/定理依据与项目自定义边界见[分类与文献依据](literature_support/CLASSIFICATION_ZH.md)。开发文档只说明当前能力与扩展接口，不包含内部人员分工。

1. [目录与代码地图](docs/DEVELOPMENT_ENTRY_ZH.md)：每个文件夹的职责，哪些文件属于数学 Core。
2. [读取配置](docs/BUSINESS_READING_CONFIG_ZH.md)：推荐起点、兼容默认和实验的边界。
3. [新增能力规则](docs/EXTENSION_MAINTENANCE_ZH.md)：能力登记、读取登记、原生证明和验收义务。
4. [当前范围](docs/CURRENT_SCOPE_ZH.md)、[数学与文献导航](docs/MATH_AND_EVIDENCE_ZH.md)：原生能力与自然语言接入并非同一范围。
5. [本次交接验收](docs/DELIVERY_READINESS_ZH.md)、[未解决项](docs/KNOWN_LIMITATIONS_ZH.md)。

五类当前短引用读取家族已共用[读取组件登记](docs/FACT_READING_REGISTRY_ZH.md)：固定政策均值、两政策差值、局部效应、R3 观察性政策、变量 DAG。它们仍各自保持目标与科学审核，登记不是数学求解器，也不会自动批准条件。

## 修改后的检查

```powershell
python -m pip install -e ".[test,documents]"
python scripts/check_framework.py --suite quick --output outputs/quick_check
python scripts/check_framework.py --suite chain --output outputs/chain_check
python scripts/check_framework.py --suite full --output outputs/full_check
python scripts/check_offline.py
```

按改动范围选层级，具体见[测试职责](docs/TESTING_ZH.md)。`[test]` 中的 Torch 用于历史兼容夹具；三个入门示例无需它。离线检查不能替代真实 LLM 准确率测量。

## 历史内容

当前操作指南在 `docs/`。内部任务安排、分轮实验日志和旧发布记录不随本仓库分发。`examples/legacy/` 中保留必要的冻结兼容夹具，其中两份模型回答只用于离线回放。大批在线输入输出仍保存在源码外，不随此包交付。`predevelopment/`、`research_partial/` 是保留旧导入的原型，正式 PARTIAL 位置见代码地图。协议内部标识不随文件整理更名，以保持请求、审核和证书兼容。
