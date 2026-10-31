# 共同事实读取登记与扩展

所有当前 **short_refs** 事实读取家族已接入 `cfm_id_llm.fact_reading_contracts.registrations()`。登记配对既有组件，不解释业务、不审批条件、不增加数学能力。学生从 `cfm_id.project` 开始，配置见[唯一推荐配置](BUSINESS_READING_CONFIG_ZH.md)。

| 读取家族 | 事实实现与特殊边界 | 业务适配器 |
|---|---|---|
| 固定政策均值 | `network_fact_protocols` 拥有既有配置表；单个完整政策、评价范围与信息角色 | `network_policy_dispatch` / 有限有界适配 |
| 两政策差值 | `network_contrast_reading` 复用政策组件；保留差值专属方向、共同评价范围、联合模型检查 | `network_contrast_dispatch` |
| 随机化局部效应 | `readers/local_effect_lifecycle` 配对 legacy / role / owned / scoped 既有实现；解析须消费已审核局部请求 | `network_effect_dispatch` |
| R3 观察性政策 | `network_observational_policy_reading`；固定背景须跨阶段独立交接 | `network_observational_policy_dispatch` |
| 变量 DAG | `dag_query_reading`；保留干预值、查询范围及原生投影 | `dag_method_dispatch` |

这是读取合同的分类，不是业务用户必须选择的五种数学方法。数学覆盖仍只有 `cfm_id.capability_registry` 一处运行登记；一份读取合同可能交给多个已有数学方法检查。

## 一份登记贯穿哪些环节

```text
已审目标 → business_dispatch.prepare_reader → 登记的请求工厂
                           ↓
原始回答 → model 格式诊断 / 来源工作表 → 原生解析与业务适配
                           ↓
显式复查取同一来源目录和字段约束 → 全部变化重新审核
                           ↓
目标交接、A4/A5、适用域检查 → 原数学入口 → 独立 replay
```

| 登记组件 | 责任 |
|---|---|
| `make_request` / `request` | 请求工厂及配置；既有方向和局部角色说明继续由原有装饰步骤加入 |
| `model`、`parse` / `parse_candidate` | 输出格式与实际解析；局部效应通过 `contextual_parse` 接收已审查询，不从模型答案批准目标类别 |
| `reference_catalog`、`documents` | 来源目录与材料定义；来源工作表和重读使用同一拥有者 |
| `field_constraints` / `contextual_constraints` | 公开诊断与重读帮助；不能读取参考答案 |
| `target_context` | 显式跨阶段目标条件交接；R3 保留独立审核项，不因字符串相同自动批准 |
| `clarify_comparison` | 两政策差值方向说明；首次与重读共同使用 |
| `profile_field`、`profile`、`wire_version` | 区分请求配置与输出版本；未知值拒绝，不静默退回默认 |

配置模块仍拥有各自的协议表：政策归 `network_fact_protocols`，局部效应配对归 `readers/local_effect_lifecycle`。公共登记消费它们，不复制第二份版本表。局部 A0 说明归 `compact_response_contract.LOCAL_PROFILE_MODULES`；增加协议必须连同 Schema、审核、诊断、重读一起验收。

## 兼容与数学边界

- 旧 hash 来源 DAG 接口继续走明确的兼容分支；不伪装成 short_refs 登记。旧显式数学/研究接口保留。
- 原生编译、求解、科学审核和独立验证函数未改变。局部目标、DAG 限制也没有因为统一登记而被抹平。
- 两政策差值仍是**第一政策减第二政策**；共同评价名单、权重和信息模型必须独立审核。联合 sharp 界不能通过两个边际区间相减替代。
- 明示错误协议阻断；历史最小调用允许省略原本可选元数据，仍按原接口验收。改变材料、配置或目标后旧批准失效。
- 共同登记不意味着所有原生目标都已接入自然语言，也不把当前未覆盖当成非识别证明。

## 实验配置与验收

`network-policy-definition-refs-1` 是显式实验选项：直接主张引用与编码/名册定义依赖分别保存，定义不能变成新的总体信息，也不能自动补目标或覆盖名单。本轮不提升它或其他实验配置为学生默认。

既有 R3、政策均值、差值合同测试分别在 `test_fact_reading_contracts`、`test_policy_reading_contracts`、`test_contrast_reading_contracts`。局部效应与 DAG 的原生正负例继续由原专项测试负责；`test_student_handoff` 检查五类共同登记、公共配置和三个教学链路。固定框架的 S87 只是验收索引，不是新数学分类。

新增能力要提交哪些证明、接口和测试见[维护规则](EXTENSION_MAINTENANCE_ZH.md)。最新实际成绩统一见[本次交接验收](DELIVERY_READINESS_ZH.md)；本页不累积每轮测试计数。
