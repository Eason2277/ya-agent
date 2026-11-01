# 项目进度与续做入口

> 更新日期：2026-11-01（Asia/Shanghai）
> 用途：让后续 AI 或开发者快速恢复项目状态。这里记录当前事实和下一步，不替代产品概要、MVP 规格或技术决策。

## 当前目标

基于 Python、LangChain 和 LangGraph 学习并原型化一个综合办公 Agent。当前选定的第一个验证场景是：制造业企业售后工单处理 Agent，结合授权的产品资料整理问题、依据、待补信息和回复草稿。

## 已确认方向与工作假设

- **技术学习主线（已确认）：** Python、Pydantic 和 LangChain 已用于当前原型；需要显式多步状态和人工审核时用 LangGraph；需要 HTTP 接口时再加 FastAPI。
- **参考代码（已确认）：** `hermes-agent/` 是本地参考克隆，不是当前 MVP 的运行时，也不属于公开项目提交内容。
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
- `examples/x100_case.md` 提供完全虚构的 E18 工单与手册摘录。`examples/first_deepseek_call.py` 已通过 LangChain 调用 DeepSeek，生成结构化 `TicketReview`，逐条调用 `src/ya_agent/evidence.py` 的 `verify_quotes` 核对引文。`src/ya_agent/review.py` 已定义 `build_review_prompt`，尚未接入示例调用。
- 已观察到完整 `TicketReview` 生成、引文核对通过，也出现过一次引文不匹配而被程序阻止的情况；模型还曾生成资料未支持的操作建议和未执行的服务承诺。提示词已收紧，但尚不能保证整份草稿安全可用。

## 下一步（一次只做一小步）

1. 将 `build_review_prompt(ticket_text, manual_text)` 接入现有示例，明确区分客户描述与指定资料；先检查函数的输入、输出和实际调用路径。
2. 将已经跑通的模型调用和引文核对逐步移入可复用的应用处理函数，形成输入工单与资料、返回待审核 `TicketReview` 的一条流程。
3. 继续核对未获资料支持的操作建议、对外承诺和失败恢复；真实客户资料的授权及模型数据路径未确认前只使用虚构或获准脱敏样本。

当前学习方式与代码注释要求见根目录 [`AGENTS.md`](../AGENTS.md)。

## 当前工作区与协作注意事项

- 远端 `main` 已推送 `aebb73b`（完整的 `schemas.py`）。本次售后方向文档、LangChain 原型和依赖变更正在准备提交/推送；提交前核对暂存区中的版本。
- 根目录 `AGENTS.md` 含用户明确要求的教学协作规则；用户亲自学习代码，未经明确要求不代写后续练习。
- 项目根目录的 `.env` 存放本地 DeepSeek API key，已被 Git 忽略；仓库只保留不含密钥的 `.env.example`。
- 不要把真实客户资料发给模型或提交到公开仓库；先用虚构或获准脱敏的材料。

## 尚未完成/未验证

- 尚未形成可供售后人员使用的完整应用；LangGraph、FastAPI、人工审核界面和外部系统集成都未实现。
- 引文检查目前只验证 `evidence.quote` 是否逐字出现在指定资料文本中，尚不能验证来源名称、结论是否受引文支持，或回复草稿的所有事实与承诺。
- 真实客户资料的数据授权、模型处理与保留策略、部署方案仍未确定。
- 未运行测试套件；当前检查来自虚构样本的手动调用和输出核对。
