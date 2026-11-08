# 决策 0004：Python 核心 + FastAPI 本地服务 + Electron/React 桌面壳，并同时提供 `ya` CLI

- 日期：2026-11-01
- 状态：已确认（用户当日明确要求确定入口与前端方案）
- 关系：细化决策 0002 中"需要服务层时用 FastAPI"一句，不改变 Python + LangChain + LangGraph 主线和决策 0003 的产品场景。

## 背景

用户明确的产品形态要求：

1. 在终端输入 `ya` 就能启动这个 Agent，交互方式参照 Hermes CLI；
2. 同时提供图形界面，让非开发者用户（如售后支持人员）能自己使用。

当前代码只有 `src/ya_agent/` 三个模块（schema、prompt 构造、引文核对）和 `examples/` 下的脚本，**没有入口层、没有 HTTP 层、没有 UI**。因此本决策要解决的是"入口和界面怎么长"，不是"改用别的技术栈"。

## Hermes 官方做法（事实，核对于 commit `944799a`，2026-11-01）

| 项 | 事实 |
| --- | --- |
| 桌面端位置 | `apps/desktop/`，`productName: "Hermes"`，描述为 "Native desktop shell for Hermes Agent" |
| 桌面端技术 | Electron 44 + React 19 + Vite + TypeScript + Tailwind 4 + shadcn/ui + electron-builder |
| 桌面端与后端关系 | `apps/desktop/electron/` 下集中了 `backend-child.ts`、`backend-discovery.ts`、`backend-health.ts`、`backend-ownership.ts`、`backend-dial-claim.ts`、`api-transport.ts`：**壳负责启动/发现/健康检查/回收一个 Python 后端进程，业务通过 API 通信** |
| Python 交付方式 | `npm run payload` → `scripts/build/python.mjs ... --out build/agent-payload`，把 Python 核心打进安装包 |
| 其他入口 | `hermes_cli/`、`cli.py`（CLI）与 `gateway/`（多渠道消息入口） |

结论：Hermes 的 Python 后端与桌面界面分离，桌面壳管理后端进程。这是入口分层的参考，不表示 Ya Agent 要照搬其通信协议或进程管理代码。Hermes 桌面端使用 JSON-RPC/WebSocket；下文的 HTTP，以及可能按需使用的 SSE，是 Ya Agent 自己的待验证选择。

## 决定

**一个 Python 核心，CLI 与 API 两个业务入口；浏览器页面和 Electron 桌面壳都通过 API 使用核心。**

```
 ya (CLI, Typer) ──────────────────────┐
                                      ├──► ya_agent.core ──► LLM / 资料检索
 浏览器页面 / Electron + React ──► FastAPI ┘    无 UI 假设
                              本地 HTTP；流式输出按需使用 SSE
```

| 层 | 选定技术 | 说明 |
| --- | --- | --- |
| 核心 | Python 3.14 + Pydantic + LangChain（LangGraph 按需） | 沿用决策 0002，不新增 |
| CLI 入口 | Typer；Rich 与 prompt_toolkit 按实际交互需要加入 | `ya` 由 `pyproject.toml` 的 `[project.scripts]` 注册；S1 先完成一条工单的最小输入/输出 |
| 服务入口 | FastAPI + Uvicorn，流式输出按需使用 SSE | 只监听 `127.0.0.1` |
| 渲染层 | React + TypeScript + Vite；样式、组件和请求库按 S2 实际需要选择 | 先用浏览器验证，桌面阶段复用主要界面代码并另行验证集成 |
| 桌面容器 | Electron + electron-builder | 参考 Hermes 的桌面进程管理经验，按本项目需求实现 |
| Python 打包 | PyInstaller 产物作为 Electron payload | 最后阶段才做 |

CLI 默认**进程内直接调用核心**（不经 HTTP）：少一跳、断点调试直观。将来需要"常驻 daemon + 多入口共享"时，再加 `ya --remote` 走同一套 API 客户端。

## 理由

### 1. 为什么先把核心与入口分离

你的两个需求（CLI 和 GUI）本质上是"同一套行为，两种呈现"。如果 `core` 里出现 `print`、`input`、`sys.argv`、或直接 `import typer/fastapi`，桌面端就只能重写一遍业务逻辑，两套实现会立刻分叉——CLI 修了提示词，桌面端没修。这是本项目当前最便宜、收益最高的一次结构投入。

### 2. 为什么 CLI 用 Python，不用 Node

- 与核心同进程，不需要额外起服务，`ya` 一条命令就能跑；
- 你在学 Python，CLI 是最短的完整练习：参数解析、异步流式输出、错误呈现；
- Rich 处理"流式文本 + 状态表格 + 证据对照"很顺手；prompt_toolkit 适合多行粘贴工单。

### 3. 为什么 GUI 用 Web 技术渲染，不用 Qt

当前审核界面需要并排核对工单、资料和草稿，还要呈现未确认事项与失败状态。先用浏览器页面实现并验证这些交互，可复用用户已有的 Web 开发经验；是否需要流式增量、工具卡片等交互，应由实际工作流决定。桌面端采用 Web 渲染层和薄壳是本项目已选的实现方案，并非所有 Agent 应用的唯一做法。

### 4. 为什么 Electron，而不是 Tauri

- Hermes 的 `backend-discovery`、`backend-health`、`backend-ownership` 等实现可供研究进程发现、健康检查和退出回收；Ya Agent 的 API 协议与生命周期要求不同，需按实际实现逐项验证，不能直接搬用；
- 不需要引入 Rust（当前学习目标是 Python 与 AI 应用；同时引入 Tauri 会增加另一门语言和运行时的学习成本）；
- Electron 能复用 S2 的主要 Web 界面代码，但仍要处理 Python 子进程、权限、打包和升级，不能假设浏览器版本可直接原样发布为桌面应用。

代价包括安装包大小、内存和进程管理；这些代价对目标售后团队是否可接受尚未验证。**若部署条件要求更轻量的客户端或集中式 Web 访问，重新比较 Electron、Tauri 和纯浏览器方案，并实测打包与维护成本。**

### 5. 为什么 React，不是 Vue

- 用户已有 React 经验；Hermes 的 React 实现也便于作为具体架构对照。当前选 React 是项目选择，不表示 AI 应用岗位普遍排斥 Vue。[腾讯的相关前端岗位](https://careers.tencent.com/zh-cn/jobdesc.html?postId=2088182151676870656)明确接受 Vue、React 或 Angular。
- TypeScript 可以帮助检查审核界面与后端数据结构的接口约定；这项收益须在 S2 的实际字段变更和联调中验证。

### 6. 为什么不选现成 UI 框架

- **Streamlit / Gradio**：适合迅速做验证界面，也能实现部分审核交互；若本项目需要细致的证据对照、可编辑草稿和浏览器到桌面的界面复用，自有 Web 页面更易按需求控制。此判断仍需用 S2 的实际交互验证。
- **PySide6 / Qt**：单一语言是优点，但会增加另一套界面实现，与本项目已选择的浏览器优先路线复用较少；若目标用户环境要求原生桌面控件，可重新评估。

## 市场与趋势判断（区分证据强度）

- **已记录的岗位样本**：决策 0002 的 2026-10-27 小样本和[2026-11-08 招聘方官网样本](../research/2026-11-08-ai-application-jobs.md)都出现业务落地、模型/工具接入、工作流和评测要求；语言与框架选择因岗位而异。样本有选择偏差，不能用“普遍”“最多”描述全市场。
- **可观察的实现案例**：Hermes 选择了 Electron + React 桌面壳 + Python 核心。这证明一种可行组合，不证明它是 AI 应用岗位通用门槛，也不证明 Ya Agent 的目标售后团队需要本地桌面部署。
- **本项目判断**：对应用岗位更可迁移的展示证据是能解释业务输入、API/状态、评测、失败恢复和人工审核的完整流程；React 体现用户已有前端能力，Electron 只有在具体交付场景要求时才产生额外价值。

## 关键约束（比技术选型更重要）

- `core/` 不得 import `typer`、`fastapi`、`rich`；不得 `print`、`input`、读 `sys.argv`。
- `core/` 对外函数接收明确入参、返回 Pydantic 模型，不返回"已经排版好的字符串"。
- CLI 与 API 都是薄层：只做 I/O、格式化、错误呈现、取消。
- 桌面壳零业务逻辑；所有判断在服务端。
- 本地服务只监听 `127.0.0.1`；使用启动时生成的随机 token 校验请求，并限制浏览器来源，检查跨站请求和 token 的传递、存储与日志。仅绑定回环地址或加入 token 都不能保证阻止本机其它进程访问客户资料；接入真实资料前必须验证实际访问边界。
- 首版 GUI 仍是**审核面板**：证据可见、待确认项显式、发送/写入外部系统的动作一律只给"复制/导出"。

## 分阶段与关卡

| 阶段 | 内容 | 关卡（进入下一阶段的条件） |
| --- | --- | --- |
| S0（当前） | `examples/` 脚本跑通模型调用与引文核对 | 已观察到一条虚构样本产出完整 `TicketReview`；无依据操作建议和服务承诺仍是待解决风险，不代表结果可直接使用 |
| S1 | 完成可复现评估；把核心接入最小 `ya` CLI | `core` 无界面 I/O 假设；CLI 能完整跑一条工单；用虚构样本检查无依据建议、对外承诺和升级情形，并把风险显式呈现给审核人。丰富的终端交互在确有使用需要时再做 |
| S2 | FastAPI `POST /reviews`；需要增量输出时再加 SSE；浏览器审核页面先当 UI | 用户能提供输入和资料、核对证据、编辑/导出草稿，并看清失败/取消态；未审核草稿不会被当作可直接发送的结论。这是首个可展示的应用闭环 |
| S2b（应用工程验证） | 按审核恢复需求实现数据保存、接口验证、必要权限与可复现部署 | 用虚构数据证明刷新/失败后可恢复；开发者能解释数据模型、API、模型调用、评测和运行边界。数据库与部署方式按实际约束选择，见决策 0005 |
| S3 | Electron 壳加载 S2 页面，自动启动本地后端 | 双击打开能跑通同一条工单；退出不留孤儿进程 |
| S4 | Python payload + 目标平台打包；签名/更新及其他平台按分发需求加入 | 在目标用户设备上装得上、能按实际交付要求维护 |

**不要在 S2 之前动 Electron。** S2 之前 `TicketReview` 还会变，每次变都要同时改前后端两处；用浏览器渲染可以让 UI 改动成本降到最低。S2b 是为应用全栈能力设置的工程验证关卡，若目标售后团队不需要跨会话保存，应把其学习实验与产品 MVP 状态区分。

**2026-11-08 的优先级补充：** 用户确认求职方向为 AI 应用岗位。[官方岗位小样本](../research/2026-11-08-ai-application-jobs.md)强调应用交付、接口、评测和业务效果；Electron 只出现在个别具体岗位，不能作为提前做桌面壳的市场理由。CLI 与桌面形态仍按用户已确认的产品方向保留，S1 先做最小入口，S2 优先展示人工审核的完整流程；见[决策 0005](0005-ai-application-portfolio-priority.md)。

## 风险与重新评估条件

- **项目打包链路仍待验证**：[PyInstaller 官方变更记录](https://pyinstaller.org/en/stable/CHANGES.html)显示从 6.15.0 起支持 Python 3.14，不能仅凭版本号断言必须降到 3.12。但 Ya Agent 的依赖、资源文件、Electron payload 和目标平台尚未实测；进入 S4 前先用最小脚本验证打包和启动，再依据实际失败决定是否调整 Python 版本或打包方案（核对于 2026-11-02）。
- **Electron 的进程管理是隐藏成本**：端口发现、后端崩溃重启、多开归属、孤儿进程回收、版本不匹配。可参考 Hermes 的处理方式，但需按 Ya Agent 的协议和生命周期验证。
- **注意力分散风险**：一旦开始写 UI，很容易把时间从"验证售后工作流是否有价值"挪到"界面好不好看"。`PROGRESS.md` 的下一步仍然优先。
- **重新评估条件**：如果售后团队明确要求 Web 集中部署（而非本地桌面），S3 换成"浏览器访问内网服务"，Electron 取消；如果安装包体积成为阻塞，S3 换 Tauri，渲染层不动；如果 GUI 交互最终只需要"填一个表单、看一段文本"，S2 的浏览器页面就是终态，不做桌面端。

## 下一步

`build_review_prompt(ticket_text, manual_text)` 和模型调用已进入 `core`，证据失败时保留已解析结果。先按 `PROGRESS.md` 固定 E18 的成功与失败评估记录，再实现最小 `ya` CLI，并尽快验证浏览器审核流程。
