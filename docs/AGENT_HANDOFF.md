# Ya Agent 续做交接

> 更新：2026-11-01（Asia/Shanghai）

## 当前目标与验收

用一条完全虚构的制造业售后工单和用户指定的手册摘录，逐步做出可人工审核的 `TicketReview`。事实应带来源，未知原因应保留为未知；不得自动发送回复。用户正在学习 Python 和 Agent 开发，默认每轮一个可核对的小步骤；用户明确要求代做时再直接实现。

## 已完成与关键决定

- `src/ya_agent/schemas.py` 已定义工单输入、证据、发现、待补问题、升级判断、回复草稿和汇总结果。该文件单独提交并推送：`aebb73b`。
- `examples/x100_case.md` 是完全虚构的工单和手册摘录；`examples/read_case.py` 已能读取并按标题分出工单、资料两段。这是练习脚本，固定标题切分不应视为正式输入协议。
- 已添加 `langchain`、`langchain-deepseek` 和 `python-dotenv` 依赖，`pyproject.toml` 与 `uv.lock` 有未提交变更。
- 用户明确选择使用其 DeepSeek API key。Pi Agent 配置仅作为一次性取 key 的来源；Ya Agent 根目录的本地 `.env` 保存 `DEEPSEEK_API_KEY`，被 Git 忽略，文件权限为 0600。`examples/first_deepseek_call.py` 只加载本项目 `.env`，用 `ChatDeepSeek(model="deepseek-chat")` 发出最小请求；仓库没有密钥字面值。`.env.example` 仅记录变量名。
- 示例脚本现在生成完整 `TicketReview`，并对每条 `Finding` 调用 `src/ya_agent/evidence.py` 的 `verify_quotes`；该函数在引文缺失时抛出 `ValueError`。`src/ya_agent/review.py` 已定义 `build_review_prompt(ticket_text, manual_text)`，尚未被示例脚本调用。
- Hermes 以后只通过官方 GitHub 和架构文档参考；`docs/decisions/0002-langchain-langgraph-learning-stack.md` 已记录高层架构对照。已确认原本地浅克隆 `hermes-agent/` 从项目目录移走，PyCharm 的第二个 Git 根映射也已从被 Git 忽略的 `.idea/vcs.xml` 移除。

## 已核对

- 用项目 `.venv` 的 Python 运行示例，真实 DeepSeek API 请求成功；虚构 E18 样本已生成结构化 `TicketReview`，最近一次核对引文通过。此前一次模型结果的引文未逐字匹配资料，被 `verify_quotes` 阻止；具体不匹配文本当时未记录。
- 模型曾在完整草稿中生成资料未支持的断电/拆卸建议和未执行的服务承诺；提示词已收紧，仍需继续核对。未运行测试套件，也未验证真实工单或客户资料路径。

## 当前工作区与下一步

- Ya Agent 自有代码和前期文档已推送至 `c7d067d`；本次 Hermes 在线参考文档改动尚未提交。继续前先检查 Git 状态，保留用户修改。
- 下一步：将 `build_review_prompt(ticket_text, manual_text)` 接到示例调用，随后把模型调用与核对逐步移入可复用的应用处理函数。每一步明确输入、输出、依据和失败边界；不要把 key 字面值写入仓库，也不要使用真实客户资料。
