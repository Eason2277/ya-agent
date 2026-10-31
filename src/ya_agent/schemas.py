from typing import Literal

from pydantic import BaseModel,Field

class SupportTicket(BaseModel):
    """保存售后人员提供的一条工单及已知背景"""

    # 从工单中粘贴或读取的问题描述
    description: str

    # 工单里有产品型号时填写，没有的时候留空
    product_model: str | None = None

    # 已知的使用环境或现象补充，没有的时候留空
    known_context: str | None = None

class Evidence(BaseModel):
    """保存一条来自产品资料或工单的依据，供售后人员核对。"""

    # 证据所在资料的名称，例如产品手册或保修政策。
    source_name: str
    # 能支持结论的原文摘录。
    quote: str
    # 原文所在页码、章节或段落；暂时无法定位时留空。
    location: str | None = None

class Finding(BaseModel):
    """保存 Agent 从工单和产品资料中整理出的一条结论。"""

    # 对工单问题或资料内容的简洁描述。
    statement: str
    # 标明结论是资料事实还是 Agent 推断。
    kind: Literal["fact", "inference"]
    # 支持这条结论的原文依据。
    evidence: list[Evidence] = Field(min_length=1)

class FollowUpQuestion(BaseModel):
    """保存一条建议向客户确认的问题及其原因"""

    # 向客户或内部人员确认
    question: str
    # 说明为什么这项信息可能影响工单处理
    reason: str

    # 优先级
    priority: Literal["low", "medium", "high", "critical"]

    # 阻塞情况
    blocking: bool

class EscalationDecision(BaseModel):
    """保存工单是否需要转交人工进一步处理的判断"""

    # True 表示建议升级，反之表示暂不需要升级
    should_escalate: bool

    # 说明判断原因；不升级时也写明原因
    reason: str

class ReplyDraft(BaseModel):
    """保存供售后人员审核的客户回复草稿"""

    # 准备给客户看的回复文字，尚未发送
    text: str

    # 给售后人员看的审核提醒，不属于客户回复
    review_note: str

class TicketReview(BaseModel):
    """保存一张工单的处理结果，以供售后人员核对和修改"""

    # 用简短文字概括工单问题
    summary: str

    # 问题类别
    category: str

    # 有来源依据的结论，以及仍需确认的问题
    findings: list[Finding]
    follow_up_questions: list[FollowUpQuestion]

    # 资料无法确认的事项，以及建议售后人员采取的下一步
    unknowns: list[str]
    next_step: str

    # 升级判断和待审核的客户回复
    escalation: EscalationDecision
    reply_draft: ReplyDraft









