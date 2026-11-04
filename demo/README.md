# Identification 网页演示

这是个人 Identification 仓库的实时网页入口，沿用团队演示的页面、九个示例、业务读取与后台复核流程。输出识别公式、采用条件、POINT/PARTIAL 或实际停止原因，以及独立证书重放结果。它不包含估计器、Policy、模拟器或 Notebook，也不需要它们的模型权重。

## 启动

下载完整仓库，在仓库根目录执行：

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[documents]"
.venv\Scripts\python demo/serve.py
```

Linux/macOS 将 `.venv\Scripts\python` 换成 `.venv/bin/python`。默认打开 `http://127.0.0.1:8772/`。也可以使用 `python demo/serve.py --port 8773 --no-browser`。不能直接双击 HTML 代替 Python 服务。

在页面“模型连接”中配置自己的 LongCat 或 DeepSeek Key；支持从本地 TXT 导入。密钥仅存在服务进程内存，关闭服务即清除，不写进源码或结果。启动网页、查看示例和历史结果不调用模型；点击开始读取才发起请求。默认每个服务进程最多 20 次模型请求，可用 `--max-api-calls 50` 显式调整。

## 使用与结果

- 自由输入业务，或从右侧载入示例并修改。可以附 TXT、MD、JSON、PDF、DOCX、CSV、XLSX 资料。表格默认提取字段和行数，不自动把有限样本变为总体信息；扫描 PDF 暂无 OCR。
- 后台读取目标、事实并复核来源；只有需要澄清原意或确认必要科学条件时才询问用户。审核边界与数学证书要求不变，模型复核不是科学真实性证明。
- 结果页展示公式与符号、适用条件和证书。没有代入总体数值的 POINT 不是已算出业务效果；有限模型 PARTIAL 的 sharp 性只相对于明确审核的模型成立。
- 九个示例保留原文和材料。N60 仍展示直接、同伴和局部总效应的识别；不再提供估计数据入口或估计数值。文献改编边界见 [示例说明](EXAMPLE_SOURCES_ZH.md)。
- “看验收记录”显示原团队网页此前的记录，明确标注为历史结果；修改业务后的新调用不沿用旧结果。程序不会从示例参考答案直接产生新任务的识别结果。

运行记录保存在仓库根目录 `outputs/web_runs/`，包含输入、模型原答及审核证据，应留在本机。服务仅监听本机，尚未作为多人公网服务部署；不要直接开放端口代替正式认证和访问控制。

## 目录和维护

| 位置 | 职责 |
|---|---|
| `serve.py` | 启动入口 |
| `index.html`、`app.js`、`style.css` | 页面、交互、公式与结果呈现 |
| `examples.json`、`condition_terms.json` | 合成示例、历史结果与统计术语 |
| `backend/` | HTTP、会话、模型请求、后台复核及 ID 调用 |
| `tests/` | 正负例、HTTP、隐私、审核边界和页面交互检查 |

`backend/` 调用本仓库的 `cfm_id.project`、读取合同与证书接口；不包含新数学求解器。自动读取／复核沿用原演示，经抽离后不再导入全流程 `autocfm`。测试夹具仅在 `tests/` 中使用，正式服务器不能导入参考答案。日常修改在维护源码的同名 `demo/` 中完成，验收后同步个人发布副本。

## 离线检查

```powershell
python -m pip install pytest jsonschema
python -m pytest demo/tests -q
node --test demo/tests/test_review_ui.cjs
```

这些检查不调用模型，不代表新的 LLM 准确率。识别库全量回归仍按根目录 README 运行。
