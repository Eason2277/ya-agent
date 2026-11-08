# 项目进度与续做入口

> 更新日期：2026-11-08（Asia/Shanghai）
> 用途：让后续 AI 或开发者快速恢复项目状态。这里记录当前事实和下一步，不替代产品概要、MVP 规格或技术决策。

## 当前目标

基于 Python、LangChain 和 LangGraph 学习并原型化一个综合办公 Agent。当前选定的第一个验证场景是：制造业企业售后工单处理 Agent，结合授权的产品资料整理问题、依据、待补信息和回复草稿。

## 已确认方向与工作假设

- **技术学习主线（已确认）：** Python、Pydantic 和 LangChain 已用于当前原型；需要显式多步状态和人工审核时用 LangGraph；本地 HTTP 服务与前端技术选型见[决策 0004](decisions/0004-cli-and-desktop-entry-architecture.md)。
- **架构参考（已确认）：** Hermes 只通过[官方 GitHub 仓库](https://github.com/NousResearch/hermes-agent)及其架构文档在线研究，不作为当前 MVP 的运行时；原本地浅克隆已从项目目录移走。
- **产品形态与入口分层（已确认，2026-11-01）：** 同时提供终端 `ya` CLI 和图形桌面端；一个 Python 核心、多个薄入口，桌面端只是壳，业务通过本地 FastAPI 访问核心。技术选型、分阶段关卡与重新评估条件见[决策 0004](decisions/0004-cli-and-desktop-entry-architecture.md)。
- **目标用户（假设）：** 制造业企业售后支持/技术服务人员，以及审核复杂工单的资深工程师或服务主管。
- **项目开发者与协作方式：** 用户是亲自学习和实现的开发者，并希望具备产品思维；不应要求用户以产品专员或售后专家身份独立给出未验证需求。AI 应先依据工作流提出有理由的建议，并清楚标注事实、假设和待验证项，再请用户判断或修正。详见根目录 `AGENTS.md`。
- **首个任务（用户已选择，需求未验证）：** 输入一条售后工单和用户指定的产品资料，输出问题分类、来源依据、待补信息、升级建议和回复草稿。
- **求职方向（用户已确认，2026-11-08）：** 目标是 AI 应用岗位和完整的 AI 应用全栈研发；已有前端经验是起点，后续要亲自掌握 Python 后端、API、数据、模型处理、评测与交付。招聘方官网小样本与作品优先级见[研究记录](research/2026-11-08-ai-application-jobs.md)和[决策 0005](decisions/0005-ai-application-portfolio-priority.md)；岗位要求不能证明技术市场份额或本场景的客户需求。
- **仍待验证：** 工单频率、人工首响耗时、资料可得性、售后人员对来源与输出结构的认可、部署方式和数据授权。

## 已完成

- 建立公开 GitHub 仓库：[Eason2277/ya-agent](https://github.com/Eason2277/ya-agent)。
- 完成产品概要、MVP 工作流和技术决策文档；当前售后场景选择记录于[决策 0003](decisions/0003-manufacturing-after-sales-ticket-agent.md)。
- 建立 Python 包骨架：`pyproject.toml`、`.python-version`、`src/ya_agent/`。
- 创建 `.venv` 并验证其 Python 为 3.14.0；系统 Python 为 3.14.6。
- 添加 Pydantic、LangChain、`langchain-deepseek` 和 `python-dotenv` 依赖，并更新 `uv.lock`。
- `uv run ya-agent` 已成功运行，输出 `Hello from ya-agent!`。目前这只是包入口占位代码，不是 MVP 功能。
- `src/ya_agent/schemas.py` 已定义工单输入、证据、发现、待补问题、升级判断、回复草稿和汇总结果 `TicketReview`；`Finding.evidence` 要求至少一条证据。
- `examples/x100_case.md` 提供完全虚构的 E18 工单与手册摘录。`examples/first_deepseek_call.py` 已通过 LangChain 调用 DeepSeek，生成结构化 `TicketReview`。完整提示词现由 `src/ya_agent/review.py` 的 `build_review_prompt(ticket_text, manual_text)` 构造；`src/ya_agent/evidence.py` 的 `verify_review_quotes` 遍历结果并逐条调用 `verify_quotes` 核对引文。
- 已观察到完整 `TicketReview` 生成和引文核对通过。脚本现在处理 `review is None`，并通过 `include_raw=True` 准备在下次解析缺失时显示原始回复与解析错误；此改动之后尚未再次观察到空结果，具体原因仍未知。此前模型曾把客户描述当成手册引文，或生成资料未支持的操作建议和未执行的服务承诺；当前输出不能直接作为客户回复。
- 已确定入口与界面方案（[决策 0004](decisions/0004-cli-and-desktop-entry-architecture.md)）：一个 Python 核心 + `ya` CLI + FastAPI 本地服务 + Electron/React 桌面壳，分 S0–S4 阶段；`core/` 禁止 `print`、`input`、`sys.argv` 和对 CLI/HTTP 框架的依赖。根 `README.md`、`AGENTS.md`、产品概要、MVP 文档和本文档已按此同步。
- `PRODUCT_BRIEF.md` 已明确按可核对的任务结果衡量 AI 能力、由观察到的瓶颈决定是否增加 RAG 或工作流编排；`MVP_WORKFLOW.md` 已列出虚构 E18 样本的预期行为与失败边界。虚构样本只检验工程行为，不证明真实业务价值。
- `src/ya_agent/core/review_ticket.py` 已集中提示词构造、DeepSeek 结构化调用、空解析结果处理与引文核对；示例脚本改为准备输入并调用核心。假模型的成功、空解析和无效引文路径已核对。重构后首次用虚构 E18 样本实际调用时，模型给出接近客户描述而不在手册中的引文，被程序拒绝；这不是完整成功样本。
- 2026-11-08，核心新增 `TicketReviewEvidenceError`，在逐字引文失败时保留已解析的 `TicketReview`；示例入口可显示失败摘要及原始引文错误。用户用虚构 E18 样本观察到模型把客户报告“设备运行时显示 E18，随后停机。”当作手册引文，并被拒绝；另一次调用返回完整结构化结果并通过当前逐字引文检查。这是两次运行观察，不证明输出的全部结论获资料支持。
- `tests/test_evidence.py` 用固定的客户引文与手册引文做正反对照；2026-11-08 执行 `uv run --no-sync python tests/test_evidence.py`，2 个离线检查通过。测试范围仅是 `verify_quotes` 的逐字包含边界。
- 根据用户选择的 AI 应用岗位方向，形成官方招聘小样本和决策 0005：售后场景暂不更换；先完成可复现评估、最小 `ya` 入口和浏览器审核流程；LangGraph、RAG、工具调用、Electron 分别按实际需求进入。

## 下一步（一次只做一小步）

1. 把虚构 E18 输入、手册、预期判据、已观察到的错误引文与成功输出、人工复核结论固定为可重复阅读的评估记录；再补“无依据操作/承诺”虚构样本。区分逐字引文检查与结论/草稿的语义支持检查。
2. 核对核心成功、解析失败和证据失败的可恢复行为后，实现最小 `ya` CLI；随后由开发者逐步完成 FastAPI 接口与浏览器审核页面，形成可解释的全栈应用流程。审核编辑与失败结果需要跨刷新恢复时，再设计持久化；真实客户资料的授权及模型数据路径未确认前只使用虚构或获准脱敏样本。

当前学习方式与代码注释要求见根目录 [`AGENTS.md`](../AGENTS.md)。

## 当前工作区与协作注意事项

- 续做前以 `git status` 核对当前工作树和远端状态，保留用户改动；本节不维护易过时的提交号。
- 核心处理函数已写入 `src/ya_agent/core/review_ticket.py`；其错误呈现与失败恢复仍是原型状态，继续前按当前文件和 Git 状态核对。
- 已确认项目目录中不再有 `hermes-agent/`；PyCharm 的第二个 Git 根映射已从本地 `.idea/vcs.xml` 移除。`.gitignore` 仍保留排除规则，以防将来误将上游克隆加入本仓库。
- 根目录 `AGENTS.md` 含用户明确要求的教学协作规则；用户亲自学习代码，未经明确要求不代写后续练习。
- 项目根目录的 `.env` 存放本地 DeepSeek API key，已被 Git 忽略；仓库只保留不含密钥的 `.env.example`。
- 不要把真实客户资料发给模型或提交到公开仓库；先用虚构或获准脱敏的材料。

## 尚未完成/未验证

- 尚未形成可供售后人员使用的完整应用；核心的证据异常保留已解析对象，示例脚本仍只做终端诊断，没有持久化、编辑或恢复工作流。`ya` CLI、FastAPI 服务、图形界面、LangGraph 和外部系统集成都未实现。按决策 0004/0005，当前不提前动桌面壳。
- 引文检查目前只验证 `evidence.quote` 是否逐字出现在指定资料文本中，尚不能验证来源名称、结论是否受引文支持，或回复草稿的所有事实与承诺。
- 真实客户资料的数据授权、模型处理与保留策略、部署方案仍未确定。
- 已运行 `tests/test_evidence.py` 中 2 个离线逐字引文检查；没有运行完整测试套件。核心函数此前通过本地假模型的成功、空解析和无效引文检查；2026-11-08 的用户运行分别观察到错误引文被拒绝和一次重构后的完整结构化输出。仍未系统验证来源名称、结论支持、草稿承诺或失败恢复界面。
