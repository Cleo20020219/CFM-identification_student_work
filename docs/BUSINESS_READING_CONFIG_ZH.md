# 唯一推荐读取配置

学生和新应用统一从 `cfm_id.project.start(case)` 开始。它加载包内唯一配置 [`cfm_id/configuration/reading.json`](../cfm_id/configuration/reading.json)：

```json
{
  "version": "business-reading-config-1",
  "reading_format": "compact",
  "fact_format": "short_refs",
  "assignment_semantics": "joint-assignment-law-1",
  "target_summary_contract": "target-summary-3",
  "a0_reference_contract": "compact-source-paragraphs-1",
  "a0_response_contract": "query-conditioning-1",
  "network_fact_contract": "network-source-selections-alignment-1"
}
```

本次只是选定已有配置，不改 Prompt。选择的理由是保留逐问背景、目标、比较方向和来源审核的既有合同；**不是“版本最大所以最好”，也没有证明是准确率最高的组合**。局部效应和 DAG 按已审目标选择自己的事实协议，这一网络配置并非所有家族的说明开关。

## 三种配置的地位

| 地位 | 位置 | 使用规则 |
|---|---|---|
| 唯一推荐起点 | `cfm_id/configuration/reading.json` | 新会话由 `project.start` 加载；学生不自行拼装 |
| 历史兼容默认 | `ReadingConfig()`、[compatibility_default.json](../examples/legacy/configs/compatibility_default.json) | 旧 API、旧 CLI 默认不改，继续重建旧请求；不是学生推荐起点 |
| 实验或历史配置 | 旧协议说明（历史实验记录不随发布分发）、`examples/legacy/configs/previous_research.json` | 只用于明确的比较或复现；必须连同当时请求、回答和审核使用 |

`network-policy-definition-refs-1`、`organized-reading-1` 等保留为实验配置，本次不提升默认。旧协议的内部标识参与绑定，不能因清理文件名而改写，也不能给旧会话自动套新配置。

## 实际调用

```python
from cfm_id import project
from cfm_id.business_intake import prepare_request
session = project.start(case)
request = prepare_request(session)
```

```powershell
python -m cfm_id.project config
python -m cfm_id.project start --input case.json --output outputs/new_case
```

`start` 仅生成会话和 A0 请求，不联网、不代填回答、不自动审核。其余步骤继续复用 [会话](BUSINESS_INTAKE_ZH.md) 和 [分派](BUSINESS_DISPATCH_ZH.md) 接口。三个离线示例也调用同一个 `project.start`。

`ReadingConfig` 验证配置组合，拒绝未知字段、非法值和不兼容格式。配置不包含 API Key、数学路线、预期结论或科学批准。修改配置只能创建新会话；不能搬用旧批准。

## 如何维护

只有一处推荐 JSON，读取函数负责加载与验证，文档不维护第二个配置对象。需要变更起点时，同步验收首次请求、事实读取配对、来源审核、重读、整题执行和源码外安装；原协议继续保留旧请求兼容。真实读取效果另做冻结评测。

五类事实配套均由 [共同登记](FACT_READING_REGISTRY_ZH.md) 管理；能力与适用域由 `cfm_id.capability_registry` 管理。二者职责不同，普通用户无需选择读取家族或数学方法。
