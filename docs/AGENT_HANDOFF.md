# Ya Agent 续做交接

> 更新：2026-11-03（Asia/Shanghai）

## 当前目标与验收

用一条完全虚构的制造业售后工单和用户指定的手册摘录，逐步做出可人工审核的 `TicketReview`。事实应带来源，未知原因应保留为未知；不得自动发送回复。用户正在学习 Python 和 Agent 开发，默认每轮一个可核对的小步骤；用户明确要求代做时再直接实现。

## 已完成与关键决定

- `src/ya_agent/schemas.py` 已定义工单输入、证据、发现、待补问题、升级判断、回复草稿和汇总结果。该文件单独提交并推送：`aebb73b`。
- `examples/x100_case.md` 是完全虚构的工单和手册摘录；`examples/read_case.py` 已能读取并按标题分出工单、资料两段。这是练习脚本，固定标题切分不应视为正式输入协议。
- 已添加 `langchain`、`langchain-deepseek` 和 `python-dotenv` 依赖；`pyproject.toml` 与 `uv.lock` 已随 `c7d067d` 推送。
- 用户明确选择使用其 DeepSeek API key。Pi Agent 配置仅作为一次性取 key 的来源；Ya Agent 根目录的本地 `.env` 保存 `DEEPSEEK_API_KEY`，被 Git 忽略，文件权限为 0600。`examples/first_deepseek_call.py` 只加载本项目 `.env`，用 `ChatDeepSeek(model="deepseek-chat")` 发出最小请求；仓库没有密钥字面值。`.env.example` 仅记录变量名。
- 示例脚本已生成完整 `TicketReview`。完整提示词集中在 `src/ya_agent/review.py` 的 `build_review_prompt(ticket_text, manual_text)`；`src/ya_agent/evidence.py` 新增 `verify_review_quotes`，遍历所有 `Finding` 并复用逐字引文核对。脚本在解析结果为空时显示诊断信息，在引文缺失时显示 `ValueError`。
- 新决策 0004 记录一个 Python 核心、`ya` CLI、FastAPI 本地服务和 Electron/React 界面的分阶段路线；当前仍处于 S0，尚未实现入口层或 UI。
- Hermes 以后只通过官方 GitHub 和架构文档参考；`docs/decisions/0002-langchain-langgraph-learning-stack.md` 已记录高层架构对照。已确认原本地浅克隆 `hermes-agent/` 从项目目录移走，PyCharm 的第二个 Git 根映射也已从被 Git 忽略的 `.idea/vcs.xml` 移除。
- 已确定入口与界面方案（`docs/decisions/0004-cli-and-desktop-entry-architecture.md`，2026-11-01）：一个 Python 核心、`ya` CLI、FastAPI 本地服务、Electron + React 桌面壳，分 S0–S4 阶段；`core/` 不得出现 `print`/`input`/`sys.argv` 或 CLI/HTTP 框架依赖。Hermes 桌面端对照事实：`apps/desktop/` 为 Electron 44 + React 19 + Vite + TS + Tailwind 4 + shadcn/ui，`apps/desktop/electron/backend-*.ts` 管理 Python 后端进程，`npm run payload` 把 Python 核心打进安装包（核对 commit `944799a`，2026-11-01）。

## 已核对

- 用项目 `.venv` 的 Python 运行示例，真实 DeepSeek API 请求成功；虚构 E18 样本已生成结构化 `TicketReview`。曾观察到一次 `review is None`，保护分支已实际触发；后来加上 `include_raw=True`，但此后未再次观察到空结果，因此具体原因仍未知。另曾观察到模型把客户描述当成手册引文，被 `verify_quotes` 阻止。
- 模型曾在完整草稿中生成资料未支持的断电/拆卸建议和未执行的服务承诺；提示词已收紧，仍需继续核对。未运行测试套件，也未验证真实工单或客户资料路径。
- 本轮重构后，本地虚构输入的引文正反例和提示词构造检查通过，三个改动文件语法解析及 `git diff --check` 通过；未再次调用 DeepSeek。

## 当前工作区与下一步

- 继续前先检查 Git 状态，保留用户修改。当前代码仍处于 S0 到 S1 的过渡：`core/review_ticket.py` 已接收工单、指定资料和模型，构造提示词、调用模型、处理空解析结果并核对引文；示例脚本只负责本地输入、模型配置及结果/错误显示。
- 2026-11-02 文档补充：`PRODUCT_BRIEF.md` 明确按任务结果和观察到的瓶颈决定技术投入；`MVP_WORKFLOW.md` 新增虚构 E18 样本评估卡，区分工程行为与尚未验证的业务价值。`src/ya_agent/core/review_ticket.py` 是用户正在编写的未完成草稿，本轮未触碰该文件或其暂存状态。
- 2026-11-02 外部评价核查后，`AGENTS.md` 增加事实优先、避免附和和以产品质量为判准的协作规则；根 `README.md` 明确 `ya` 是规划入口，当前只注册占位的 `ya-agent`；决策 0004 根据 PyInstaller 官方变更记录修正 Python 3.14 的打包风险描述。市场岗位样本不能推出全国需求占比。
- 2026-11-03 验证：核心函数的假模型成功、空解析和无效引文路径已核对；示例与核心语法检查通过。重构后的虚构 E18 实际调用因模型引文接近客户描述、未出现在指定手册中而被拒绝。当前只看到错误引文，尚不知道模型对应的完整结论和来源标注；失败后整份结构化结果未保留给使用者。
- 下一步：保持指定资料引文检查，对照 E18 评估卡处理来源边界与失败结果保留，然后继续验证完整成功路径，最后由 `ya` CLI 渲染（S1）。不要把 key 字面值写入仓库，也不要使用真实客户资料。
