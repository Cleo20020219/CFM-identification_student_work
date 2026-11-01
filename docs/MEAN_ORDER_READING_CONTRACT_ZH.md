# 均值顺序：统一入口的读取合同

维护入口是 `cfm_id_llm/mean_order_field_contract.py`。这里维护公开字段含义，以及已有投影器要求的字段组合；不实现数学求界，不批准科学条件。统一入口通过 `network_mean_order_reading.py` 使用它。

| 原文状态 | 读取表达 | 后续含义 |
|---|---|---|
| 明确提出均值非减条件 | NONDECREASING，并保留层级、范围和来源 | 仍须独立科学审核，不能由 LLM 批准 |
| 尚未决定是否采用、意思不清楚 | UNKNOWN，保留明确的原文信息 | 继续追问；不能改成不采用 |
| 明确不采用该非减条件 | NOT_ASSUMED；level 和 scope 均为 null | 该轴没有顺序许可；其他条件仍需审核 |
| 材料没有提及该轴 | 保留缺失，不补 NOT_ASSUMED | 逐对象、逐轴完整性检查继续阻断 |
| 明确无影响或非增 | NO_EFFECT 或 NONINCREASING | 不偷换成非减／不采用，保留现有覆盖限制 |
| 跨对象等式、其他尚未适配的限制 | 保留额外限制原文和引用 | 报告当前适配器未覆盖，不生成假认证 |

`reported_conflict` 记录材料中的科学声明是否相互矛盾。未发现矛盾可为 false；条件尚未决定、材料缺项和等待科学审核均不等于发现矛盾。它不批准任何假设。

`other_restriction_source_ids` 只保留尚未适配的真实额外限制。“除此之外没有约束”的完整性声明不是额外限制；基础科学条件、均值充分性、界限、精确均值信息及已保留的顺序也不是额外限制。

两个完整性字段的职责不同：

- `bounded_model.no_additional_coupling_constraints`：有没有额外跨安排／跨对象的耦合；已采用均值顺序时不能填 true。
- `mean_order_model.no_additional_constraints_beyond_declared_orders`：除基础条件、均值充分性、界限和已列顺序之外是否没有其他约束。原文明示无其他约束为 true，有其他约束为 false，未说明或未定为 null。某条顺序尚未决定，不自动改变这项独立声明。

所有引用仍按记录分别审核。将“名单中的每个单位”展开为具体名称时，本记录要同时引用名单定义；不得借父字段、其他记录或审核人的补充引用修复模型答案。逐单位界限和充分性的覆盖名单也遵守同一规则。

## 扩展与验收

`NULL_RULE` 是 NOT_ASSUMED 组合约束的唯一读取端定义，由它生成 JSON Schema 条件、解析检查和错误诊断。复查通过共同读取登记，从首次请求 Schema 读取字段规则；审核工作表也显示相同规则。诊断只定位字段和公开约束，不给出该题替换值，不修补原答。

数学投影仍使用原有 `cfm_id/mean_order_reading.py`，求界、独立验证器、科学审核及证书合同保持原样。未知、拒绝和覆盖不足不能当作格式错误自动修复；格式通过也不证明语义或引用正确。

本次仅更新统一入口的均值顺序读取配置。旧读取家族及 System Prompt 不变；当前配置的新请求 Schema 会改变请求绑定，新请求必须重新读取和审核，不能套用旧请求的批准记录。

定向检查：`python -m pytest -q tests_gateway/test_mean_order_field_contract.py tests_gateway/test_network_mean_order_dispatch.py`。前者检查公开／本地合同及诊断，后者覆盖 POINT、PARTIAL、假设变化、拒绝、证书篡改和旧配置兼容。真实模型效果须单独评测，不能用离线测试数替代。
