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
| CLI 入口 | Typer + Rich + prompt_toolkit | `ya` 由 `pyproject.toml` 的 `[project.scripts]` 注册 |
| 服务入口 | FastAPI + Uvicorn，流式输出按需使用 SSE | 只监听 `127.0.0.1` |
| 渲染层 | React 19 + TypeScript + Vite + Tailwind 4 + shadcn/ui + TanStack Query | 先用浏览器跑，后续原样搬进 Electron |
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

Agent 界面真正难的不是"有窗口"，而是这些：流式增量文本、Markdown 渲染、工具调用/证据的可折叠面板、`evidence.quote` 与结论的并排对照、需要人工确认的操作卡片、失败重试。这类东西在 Web 技术里全是成熟组件，在 Qt 里基本要手搓。**这也直接决定了桌面端只能是"Web 渲染层 + 薄壳"**。

### 4. 为什么 Electron，而不是 Tauri

- Hermes 的 `backend-discovery`、`backend-health`、`backend-ownership` 等实现可供研究进程发现、健康检查和退出回收；Ya Agent 的 API 协议与生命周期要求不同，需按实际实现逐项验证，不能直接搬用；
- 不需要引入 Rust（你的学习目标是 Python，Tauri 会变成第三门语言）；
- `electron-builder` 对 mac dmg / win msix / linux AppImage、自动更新的支持最成熟。

代价（实打实）：安装包 ~150MB+、内存占用高。判断：面向企业内部售后人员的工具，这个代价可接受。**若将来需要轻量分发或面向 C 端，重新评估 Tauri——渲染层代码可原样复用，只需重写壳。**

### 5. 为什么 React，不是 Vue

- Agent 前端组件生态（流式渲染、shadcn/ui、各类 chat/approval 组件）集中在 React；
- Hermes 用 React + shadcn/ui（`components.json` 为 `new-york` 风格、Tailwind 4），便于逐文件对照；
- TypeScript 让"后端 Pydantic 模型 ↔ 前端类型"的对接更可控。

### 6. 为什么不选现成 UI 框架

- **Streamlit / Gradio**：几小时能出界面，但表达不了"证据对照 + 审核门禁 + 可编辑草稿 + 失败恢复"这类精细交互，且无法演进成正式产品。只适合临时演示。
- **PySide6 / Qt**：单一语言是优点，但理由 3 里那些交互会变成大量手写控件，且 UI 无法与将来可能的 Web 版复用。

## 市场与趋势判断（区分证据强度）

- **已记录的弱证据**：决策 0002 的招聘岗位小样本显示，Agent 岗位普遍要求 Python、工具调用、工作流编排、RAG、评估；LangChain/LangGraph 被列为可接受经验。**这是小样本抽查，不是全市场统计。**
- **可观察的生态信号**：Hermes 这类成熟开源 Agent 应用选择了 Electron + React 桌面壳 + Python 核心的组合；Python + FastAPI + React 是当前 AI 应用全栈的常见形态。
- **我的判断（非事实）**：本方案里真正长期可迁移的能力仍是 Python 后端、API/状态设计、评估与可观测性；Electron/React 是可替换的展示层。因此不应该为了"技术栈好看"而把学习重心挪到前端。

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
| S1 | 把逻辑收进 `ya_agent/core/`；`ya` CLI 渲染 | `core` 无界面 I/O 假设；CLI 能完整跑一条工单；用虚构样本检查无依据建议、对外承诺和升级情形，并把风险显式呈现给审核人 |
| S2 | FastAPI `POST /reviews`；需要增量输出时再加 SSE；浏览器页面先当 UI | `TicketReview` 的当前字段足以支持审核；证据、待确认项、失败/取消态可核对，未审核草稿不会被当作可直接发送的结论 |
| S3 | Electron 壳加载 S2 页面，自动启动本地后端 | 双击打开能跑通同一条工单；退出不留孤儿进程 |
| S4 | Python payload + 三平台打包 + 签名/更新 | 在别人的电脑上装得上、能升级 |

**不要在 S2 之前动 Electron。** S2 之前 `TicketReview` 还会变，每次变都要同时改前后端两处；用浏览器渲染可以让 UI 改动成本降到最低。

## 风险与重新评估条件

- **项目打包链路仍待验证**：[PyInstaller 官方变更记录](https://pyinstaller.org/en/stable/CHANGES.html)显示从 6.15.0 起支持 Python 3.14，不能仅凭版本号断言必须降到 3.12。但 Ya Agent 的依赖、资源文件、Electron payload 和目标平台尚未实测；进入 S4 前先用最小脚本验证打包和启动，再依据实际失败决定是否调整 Python 版本或打包方案（核对于 2026-11-02）。
- **Electron 的进程管理是隐藏成本**：端口发现、后端崩溃重启、多开归属、孤儿进程回收、版本不匹配。可参考 Hermes 的处理方式，但需按 Ya Agent 的协议和生命周期验证。
- **分辨率风险**：一旦开始写 UI，很容易把时间从"验证售后工作流是否有价值"挪到"界面好不好看"。`PROGRESS.md` 的下一步仍然优先。
- **重新评估条件**：如果售后团队明确要求 Web 集中部署（而非本地桌面），S3 换成"浏览器访问内网服务"，Electron 取消；如果安装包体积成为阻塞，S3 换 Tauri，渲染层不动；如果 GUI 交互最终只需要"填一个表单、看一段文本"，S2 的浏览器页面就是终态，不做桌面端。

## 下一步

`build_review_prompt(ticket_text, manual_text)` 已接进示例。先处理当前暴露的结构化结果缺失与引文混用，再把已核对的逻辑收进 `core`；`ya` CLI 随后作为第一个薄入口渲染结果。具体下一小步见 `PROGRESS.md`。
