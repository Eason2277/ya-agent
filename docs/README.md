# Ya Agent 文档

项目级协作和范围规则见根目录 [`AGENTS.md`](../AGENTS.md)。

## 文档索引

- [项目进度与续做入口](PROGRESS.md)：当前状态、已完成事项、工作区注意事项和下一步。
- [产品概要](PRODUCT_BRIEF.md)：综合办公产品方向、当前用户假设、原则与待验证问题。
- [MVP 工作流](MVP_WORKFLOW.md)：当前选定的制造业售后工单处理 Agent、范围和验收方式。
- [技术决策 0002](decisions/0002-langchain-langgraph-learning-stack.md)：当前 MVP 的 Python、LangChain、LangGraph 技术选择，以及 Hermes 官方架构的在线对照。
- [历史决策 0001](decisions/0001-hermes-agent-foundation.md)：记录早期考虑以 Hermes 为基础及客户访谈场景；底座由决策 0002、首个产品场景由决策 0003 取代。
- [当前场景决策 0003](decisions/0003-manufacturing-after-sales-ticket-agent.md)：选择制造业售后工单处理 Agent 作为首个 MVP 验证切片。
- [入口与前端决策 0004](decisions/0004-cli-and-desktop-entry-architecture.md)：Python 核心 + `ya` CLI + FastAPI 本地服务 + Electron/React 桌面壳的分层方案与分阶段关卡。

当前工作流已选作 MVP 验证起点，但用户痛点和产品价值尚未验证。产品和技术文档应持续区分决定、假设与证据。
