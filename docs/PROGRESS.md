# 项目进度与续做入口

> 更新日期：2026-11-02（Asia/Shanghai）
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

## 下一步（一次只做一小步）

1. 对照 `MVP_WORKFLOW.md` 的虚构 E18 评估卡，将示例中的模型调用、结构化解析和 `verify_review_quotes` 逐步移入可复用的应用处理函数（`ya_agent/core/`），形成输入工单与资料、返回待审核 `TicketReview` 的流程。失败时保留可诊断的信息，由入口决定如何显示；`core` 内不得出现 `print`、`input`、`sys.argv` 或 CLI/HTTP 框架依赖。
2. 让 `ya` CLI 成为第一个薄入口，用虚构样本检查完整流程，再继续核对无依据操作建议、对外承诺和失败恢复。真实客户资料的授权及模型数据路径未确认前只使用虚构或获准脱敏样本。

当前学习方式与代码注释要求见根目录 [`AGENTS.md`](../AGENTS.md)。

## 当前工作区与协作注意事项

- 续做前以 `git status` 核对当前工作树和远端状态，保留用户改动；本节不维护易过时的提交号。
- `src/ya_agent/core/review_ticket.py` 有用户正在编写的未完成草稿；本轮文档修改没有改动或暂存该文件。继续实现前按当前文件内容核对，不把草稿视为已运行的核心流程。
- 已确认项目目录中不再有 `hermes-agent/`；PyCharm 的第二个 Git 根映射已从本地 `.idea/vcs.xml` 移除。`.gitignore` 仍保留排除规则，以防将来误将上游克隆加入本仓库。
- 根目录 `AGENTS.md` 含用户明确要求的教学协作规则；用户亲自学习代码，未经明确要求不代写后续练习。
- 项目根目录的 `.env` 存放本地 DeepSeek API key，已被 Git 忽略；仓库只保留不含密钥的 `.env.example`。
- 不要把真实客户资料发给模型或提交到公开仓库；先用虚构或获准脱敏的材料。

## 尚未完成/未验证

- 尚未形成可供售后人员使用的完整应用；`ya_agent/core/` 只有未完成草稿，`ya` CLI、FastAPI 服务、图形界面、LangGraph 和外部系统集成都未实现。按决策 0004，当前不提前动桌面壳。
- 引文检查目前只验证 `evidence.quote` 是否逐字出现在指定资料文本中，尚不能验证来源名称、结论是否受引文支持，或回复草稿的所有事实与承诺。
- 真实客户资料的数据授权、模型处理与保留策略、部署方案仍未确定。
- 未运行测试套件。提示词集中和整份结果引文核对改动已通过本地虚构输入的正反例、三个改动文件的语法解析及 `git diff --check`；此次重构后未再次调用 DeepSeek。
