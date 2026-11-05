# 任务7：七类审查导航表

基线提交：7a4cb948ee28c74e4bbf1f2f561de74ff4ce6d6a

导航来源：
literature_support/mathematical_contracts.json

说明：
所有路径相对于仓库根目录。
索引定位完成不等于文件内容已核查，
也不等于数学正确性或测试通过已得到确认。

## 一、七类数学文档

| 审查对象 | 优先阅读的项目数学文档 |
|---|---|
| R1a | docs/ABSTRACTION_RANDOMIZED_ARM_ZH.md；docs/R1A_VERIFIED_TARGET_COMPOSITION_ZH.md |
| R1b | docs/R1B_VERIFIED_FULL_ASSIGNMENT_POLICY_ZH.md；docs/NETWORK_CONTRAST_DISPATCH_ZH.md |
| R2 | docs/R2_VERIFIED_MEAN_SIGNATURE_POLICY_ZH.md；docs/R2_POLICY_DIFFERENCE_CONTRACT_ZH.md |
| R3-Full | docs/R3_OBSERVATIONAL_FINITE_POLICY_AND_SIGNATURE_DIAGNOSTICS_ZH.md；docs/R3_POLICY_ENTRY_CONTRACT_ZH.md |
| D2/E1 单政策界 | docs/BOUNDED_POLICY_MATH_ZH.md |
| 两政策联合差值界 | docs/BOUNDED_CONTRAST_MATH_ZH.txt |
| 均值顺序差值界 | docs/MEAN_ORDER_RESEARCH_ZH.txt |

范围提醒：
索引条目可能同时包含多个子路线或组合能力。
本表收录相关文档，不表示其中所有能力均纳入任务7。
R3 仅审指定的 R3-Full，其他 R3 子路线及 DAG 不在本批范围。

## 二、数学实现及相关组合文件

以下路径来自索引；具体职责仍需阅读确认。

### R1a

- pfn_pipeline/_internal/identification/randomized_network_arm.py
- pfn_pipeline/identification_composition.py

待确认：局部均值求解、组合检查、证书验证分别位于哪些函数。

### R1b

- pfn_pipeline/identification_policy_r1b.py
- cfm_id/fixed_comparison.py

已由项目合同定位的函数名：

- 固定政策求解/签发：
  identify_verified_fixed_policy(...)
- 固定政策重放：
  replay_verified_fixed_policy(...)
- 有限政策混合：
  identify_verified_finite_policy_mixture(...)
- 有限政策混合重放：
  replay_verified_finite_policy_mixture(...)

上述接口由 pfn_pipeline.identification_policy_r1b 提供。

固定政策签发、重放、_solve、_independent_q 和
_policy_formula 已完成静态初读。

有限政策混合及其重放函数尚未审读。

专项测试线索：

- tests/test_verified_fixed_policy_r1b.py

示例入口：

- examples.run_verified_r1b_fixed_policy

当前状态：

已完成合同初读、固定政策主要函数静态初读；
已有 R1b 专项测试实际运行28项，全部通过。

D1、D2 支持概率公式已与手算对照；
其他设计分支及共享依赖未完成核查。

本任务独立计算程序和证书专项检查尚未完成。

审查关注：

- 区分路线适用条件与一般数学必要条件。
- 检查完整安排信息与 arm-level 信息的区别。
- 检查重放与求解器之间的调用及共享依赖。
- 检查支持概率、目标、权重、假设和来源绑定。

已确认：签发与重放均调用 _solve。
支持概率另由 _independent_q 与 AssignmentSpec 交叉核对；
D1、D2 算式已静态核对；
其他设计分支及共享依赖待审。

已有专项测试运行：

tests/test_verified_fixed_policy_r1b.py
实际运行28项，全部通过。

已有测试的独立性与覆盖内容尚未审读；
本任务独立计算程序和证书专项检查仍未完成。

### R2

- pfn_pipeline/identification_policy_r2.py
- cfm_id/workflows/policy_difference.py

待确认：原生政策均值求解和验证函数；
区分单端识别与有序差值组合检查。

### R3-Full

- pfn_pipeline/identification_observational_r3.py

相关业务连接：

- cfm_id/network_observational_policy_dispatch.py
- cfm_id_llm/network_observational_policy_reading.py

待确认：R3-Full 的原生求解与验证入口。
业务分派、读取模块不直接视为数学求解器。

### D2/E1 单政策界

- cfm_id/bounded_policy_contract.py
- cfm_id/bounded_policy_solver.py
- cfm_id/bounded_policy_verify.py

已完成数学合同初读，与七网点手算区间一致。

文档声明重放独立枚举，不调用求解器、
SupportEngine 或其暴露分类原语；
实际实现及共享输入校验仍待核查。

### 两政策联合差值界

- cfm_id/bounded_contrast_contract.py
- cfm_id/bounded_contrast_solver.py
- cfm_id/bounded_contrast_verify.py

待确认：共同模型、共享未知量、比较方向及端点检查。

### 均值顺序差值界

- cfm_id/mean_order_contract.py
- cfm_id/mean_order_solver.py
- cfm_id/mean_order_verify.py

相关业务连接：

- cfm_id/network_mean_order_dispatch.py

待确认：顺序约束、目标差值、求解与验证的具体函数。

## 三、文献映射入口

| 审查对象 | 路线映射文件 |
|---|---|
| R1a | literature_support/routes/network_r1a.json |
| R1b | literature_support/routes/network_r1b.json |
| R2 | literature_support/routes/network_r2_policy_difference.json |
| R3-Full | literature_support/routes/network_r3_policy.json |
| D2/E1 单政策界 | literature_support/routes/bounded_policy_contrast.json |
| 两政策联合差值界 | literature_support/routes/bounded_policy_contrast.json |
| 均值顺序差值界 | literature_support/routes/mean_order_research.json |

路径提醒：
路线 JSON 中的 derivation_path 相对于该路线 JSON 所在目录，
不能一律按仓库根目录解释。

## 四、当前进度

| 审查对象 | 文档与实现路径 | 教学输出初读 | 独立计算程序 | 验证器专项检查 |
|---|---|---|---|---|
| R1a | 索引已定位 | 未做 | 未做 | 未做 |
| R1b | 索引已定位 | 已做 | 未做 | 未做 |
| R2 | 索引已定位 | 未做 | 未做 | 未做 |
| R3-Full | 索引已定位 | 未做 | 未做 | 未做 |
| D2/E1 单政策界 | 索引已定位 | 已做，已讨论手算与可实现性 | 未做 | 未做 |
| 两政策联合差值界 | 索引已定位 | 未做 | 未做 | 未做 |
| 均值顺序差值界 | 索引已定位 | 未做 | 未做 | 未做 |

缺条件教学例：
已核对模型完整性声明未确认时的停止输出；
具体检查函数尚未定位。

## 五、后续需要补齐

- [ ] 阅读七类项目数学合同，记录目标、信息、假设和适用域
- [ ] 定位具体求解与验证函数
- [ ] 定位各类示例和测试
- [ ] 记录求解器与验证器共享组件的风险
- [ ] 为各类建立独立参考计算
- [ ] 检查合法证书及数学错误证书
- [ ] 分别记录已审、未审和未决问题

优先审查候选：

1. R1b：五网点全用政策 POINT 例子。
2. D2/E1 单政策界：七网点全用政策 PARTIAL 例子。