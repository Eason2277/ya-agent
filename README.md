# Ya Agent

面向综合办公场景的 Agent 学习与产品原型项目。当前先验证一条具体工作流：帮助制造业企业售后支持人员依据产品资料处理服务工单，并生成有来源依据、可审核的回复草稿。

## 当前状态

- 产品和 MVP 文档已建立。
- 技术学习与原型路线：Python + LangChain；需要显式状态或人工暂停/恢复时再用 LangGraph，需要服务接口时再引入 FastAPI。
- 规划的产品形态：终端输入 `ya` 启动的 CLI，以及自有图形界面，两者共用同一 Python 核心；分层与前端选型见[决策 0004](docs/decisions/0004-cli-and-desktop-entry-architecture.md)。当前 `pyproject.toml` 只注册了输出占位信息的 `ya-agent`，`ya` CLI 尚未实现。
- Hermes Agent 仅通过[官方 GitHub 仓库](https://github.com/NousResearch/hermes-agent)作架构参考，不在本项目保留上游源码，也不是当前 MVP 的运行时。
- 已有基于虚构工单的模型调用与引文核对示例；尚未形成可供售后人员使用的完整应用，用户痛点和产品价值仍需验证。

## 文档

- [项目协作规则](AGENTS.md)
- [项目进度与续做入口](docs/PROGRESS.md)
- [产品概要](docs/PRODUCT_BRIEF.md)
- [MVP 工作流](docs/MVP_WORKFLOW.md)
- [技术决策索引](docs/README.md)
- [入口与前端决策 0004](docs/decisions/0004-cli-and-desktop-entry-architecture.md)
- [AI 应用岗位作品优先级决策 0005](docs/decisions/0005-ai-application-portfolio-priority.md)
- [招聘方官方岗位样本与项目取舍](docs/research/2026-11-08-ai-application-jobs.md)

## MVP 概述

输入一条获准使用或脱敏的售后工单，并提供相关产品手册、服务政策或已解决案例；输出工单分类、依据、建议处理步骤、待补信息、升级建议和回复草稿。用户审核后再复制或导出。首版不自动发送回复、更新工单系统或执行设备操作。

## 开发约定

遵循根目录 `AGENTS.md` 和 `docs/` 中的产品及技术决策。先完成一条可验证的端到端工作流，再扩展集成和自动化。
