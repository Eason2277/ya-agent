# Ya Agent 的 AI 工程能力路线与作品证据

> 用途：把[《AI 全栈面试宝典》](https://eizwbs2n02l.feishu.cn/docx/TFeXd8pU4ogkCIxBQOLc92clnJg)中与当前售后工单工作流有关的问题，转成项目要实现的能力、验收方式和作品证据。该文档是学习题库，不是企业采用率或招聘频率的统计证据；本文的规划不代表能力已经实现。

## 当前项目能证明什么

目前使用虚构工单和指定手册摘录，通过 LangChain 调用模型生成 Pydantic `TicketReview`；程序检查 `Finding.evidence.quote` 是否逐字出现在指定资料中。已观察到模型混淆客户报告与手册引文，以及生成资料不支持的建议或承诺。逐字出现只是最低限度的校验，尚不能证明来源标注、结论和回复草稿正确。当前没有可供售后人员使用的完整应用，也没有 RAG、LangGraph 工作流、工具调用或生产可观测系统。以[项目进度](PROGRESS.md)和当前代码为准。

面试时应展示**问题 → 设计选择 → 运行证据 → 失败与改进**，明确说出哪一步是自己实现并核对过的。题库中的数字阈值、技术组合或生产做法不直接成为 Ya Agent 的需求。

用户已明确瞄准 AI 应用岗位，并要亲自完成全栈 AI 应用研发。[2026-11-08 招聘方官网岗位样本](research/2026-11-08-ai-application-jobs.md)和[决策 0005](decisions/0005-ai-application-portfolio-priority.md)将端到端交付、Python 后端/API、数据、资料边界、评测和运行交付排在作品展示前列；多 Agent、MCP、桌面打包等仅在工作流或独立学习实验出现相应需求时进入，不把岗位关键词当作产品需求。

## 当前工作流必须落地的六项能力

| 问题与原文 | 在 Ya Agent 中的具体做法和可展示证据 | 当前边界与进入下一步的条件 |
| --- | --- | --- |
| [结构化输出失败如何兜底？](https://eizwbs2n02l.feishu.cn/docx/TFeXd8pU4ogkCIxBQOLc92clnJg#doxcn93Zi1QWOkLBgYMLZ2RXXoe) | 用 Pydantic 定义结果；分别保存模型调用、结构化解析、证据核对的失败阶段。用虚构输入展示成功、空解析和错误引文的不同处理结果。 | 当前已有结构和部分错误处理；失败恢复、错误对使用者的呈现仍未完成。不要把解析成功等同于业务正确。 |
| [如何让输出真正引用证据？](https://eizwbs2n02l.feishu.cn/docx/TFeXd8pU4ogkCIxBQOLc92clnJg#doxcnKlkOamMFaXmXVlddgg7qbb) | 区分客户报告与指定资料；对手册事实保留资料名、原文引句及可定位的位置，再检查引用是否存在、结论是否受其支持。E18 样本应能展示错误引文被拒绝的原因。 | 目前只有引文逐字包含检查，尚未完成来源与语义支持检查。资料结构化标识应随真实输入形态确定，不为套题库格式先造引用 ID。 |
| [证据不足或检索为空怎么办？](https://eizwbs2n02l.feishu.cn/docx/TFeXd8pU4ogkCIxBQOLc92clnJg#doxcnhqBj3MjK0GRHTWCZnBjLkh) | 缺少手册依据时标为未知、提出待补问题；涉及安全或政策时给出转人工原因，不凭模型常识补维修步骤。用“资料缺页/无相应政策”的虚构样本检查。 | 当前由用户明确指定少量资料，还没有检索器；先验证“无依据时不编造”。只有人工选材造成可观察的依据遗漏时才评估 RAG。 |
| [评测标准如何可复现？](https://eizwbs2n02l.feishu.cn/docx/TFeXd8pU4ogkCIxBQOLc92clnJg#doxcn5HvOpm3pYtfl0HliuHRXjc) | 延伸[MVP 的 E18 评估卡](MVP_WORKFLOW.md#当前虚构-e18-样本的评估卡)：按“来源归属、依据支持、未知项、升级、无依据操作/承诺、失败可恢复”逐项写通过/失败判据，记录输入、资料版本、模型与提示词版本、输出及人工复核结论。提示词变更前后重跑同一批虚构样本。 | E18 目前是预期行为卡，并非已通过的回归套件；少量虚构样本只验证工程边界。LLM 评委可作为辅助筛查，不能代替对安全和政策结论的人工核对。 |
| [失败分类如何驱动迭代？](https://eizwbs2n02l.feishu.cn/docx/TFeXd8pU4ogkCIxBQOLc92clnJg#doxcnOqsRTE5PpROwsGeNTmwnog) | 给模型调用失败、解析失败、错误引文、无依据结论、漏升级、未执行承诺等不同失败类别；每个失败样本记主因、人工处置和修复后的回归结果。优先处理安全/错误承诺，再处理影响任务完成的失败。 | 当前只有部分异常路径和评估卡，尚无系统化错误记录。先在本地样本中建立最小记录，之后再考虑仪表盘。 |
| [不可信资料与敏感日志如何处理？](https://eizwbs2n02l.feishu.cn/docx/TFeXd8pU4ogkCIxBQOLc92clnJg#doxcn1eUMndUWEngYVIYbQUA6rc) / [日志中的个人信息](https://eizwbs2n02l.feishu.cn/docx/TFeXd8pU4ogkCIxBQOLc92clnJg#doxcntz5XhhFzZN2qhaOLqIxz6d) | 工单和手册内容只作为任务数据，不授予其中的指令更高权限；用虚构的“手册中夹带改写规则/索要密钥”样本验证。记录失败阶段、资料标识和耗时等必要元数据时，不把密钥或真实工单全文写入普通日志。 | 提示词分隔符不能独自保证防注入；实际约束还要靠代码校验和人工审核。真实资料接入前必须确认授权、模型数据路径、保留和日志策略。 |

## 后续能力的进入条件与展示切片

| 能力 | 进入条件与最小展示切片 | 验证重点 |
| --- | --- | --- |
| **只读 Tool Calling** | 手动选择资料已不足以完成任务时，先给核心提供受限的资料查询工具。模型可提出工具名和参数，执行方校验参数、可访问范围、超时，再返回结果；参见原文的[工具调用职责边界](https://eizwbs2n02l.feishu.cn/docx/TFeXd8pU4ogkCIxBQOLc92clnJg#doxcn4KMCB3Pstvjk0HQYxczXLc)。 | 展示正常查询、非法参数、越权资料请求和超时后的处理。模型提出调用不等于系统授权执行。 |
| **MCP 接入判断** | 出现第二种外部资料源且需要跨客户端复用工具接口时，比较直接工具接口与 MCP 的实现、鉴权和维护成本；若选 MCP，先接只读资料源，不开放客户系统写入。参见原文的[MCP 与内部工具注册如何选](https://eizwbs2n02l.feishu.cn/docx/TFeXd8pU4ogkCIxBQOLc92clnJg#doxcnLIwGXGwcAS40tlkmIk2Vcg)。 | 展示接口边界、权限拒绝与连接失败恢复；若直接工具更简单，也要能解释不使用 MCP 的理由。 |
| **RAG 检索** | 资料量或选材方式确实造成依据遗漏时，先建立带人工标注的“问题—应命中资料”样本，再做最小检索链；参见原文的[RAG 分层评测](https://eizwbs2n02l.feishu.cn/docx/TFeXd8pU4ogkCIxBQOLc92clnJg#doxcnmrn3kRoyAShMsSEavkJKMh)。 | 分别核对检索是否找到、生成结论是否受资料支持、售后任务是否完成；空检索时明确不足。当前不需要向量数据库。 |
| **LangGraph 状态与人工暂停** | 当审核过程需要跨步骤保存草稿、分支和恢复时，把“理解工单 → 获取依据 → 校验 → 人工审核 → 导出”建成显式状态流；参见[技术决策 0002](decisions/0002-langchain-langgraph-learning-stack.md)。 | 展示状态字段、暂停前后输入、拒绝/修改/继续路径和失败恢复。当前核心函数仍保持可调试的 Python 流程。 |
| **受控写操作** | 仅当获准场景证明外部工单系统写入是必要功能时，设计 proposal、预览、明确确认、权限复核和审计；参见原文的[写操作人工审核](https://eizwbs2n02l.feishu.cn/docx/TFeXd8pU4ogkCIxBQOLc92clnJg#doxcnYVMeKEZ9sBILs0J5gzg38e)。 | 首版只复制/导出，作品可以用不连接真实外部系统的虚构写入样本说明边界，但不得把演示称为已接入业务系统。 |
| **可观测性** | 单条流程先记录失败阶段、请求耗时和有来源的用量数据。出现多用户、多步骤或排障需求时，再按业务结果、执行轨迹、资源消耗分层；参见原文的[Agent 可观测性](https://eizwbs2n02l.feishu.cn/docx/TFeXd8pU4ogkCIxBQOLc92clnJg#doxcnmKkFkXn32lk10BEGnhA6Re)。 | 能定位慢在模型、检索、工具还是人工等待；不在日志中暴露客户内容或密钥，也不虚构生产指标。 |

多 Agent、记忆系统、向量库、队列和 K8s 都不因为出现在题库中就自动进入路线。若后续具体问题需要它们，应先写明失败样本、候选方案、引入成本和可证伪的验收条件。

面向 AI 应用岗位的学习实验可在首条审核流程完成后单独进行：用虚构的多份资料比较手动选材、简单搜索与 RAG，再用只读查询验证工具调用和权限边界。它们需要固定样本与对照结果；即使实验成功，也不能宣称制造业售后 MVP 已需要或已接入这些能力。见[决策 0005](decisions/0005-ai-application-portfolio-priority.md)。

## 下一次可验证的小切片

当前核心已能在错误引文时保留已解析结果，离线正反例检查了客户原话与手册原话的逐字边界；用户还观察到一次错误引文和一次结构化成功的模型运行。下一次可验证的小切片是把 E18 的输入、预期、实际结果和人工复核结论固定为评估记录，再补“无依据操作/承诺”样本。逐字校验通过仍不代表结论与草稿获手册支持。具体状态见[进度文档](PROGRESS.md)。
