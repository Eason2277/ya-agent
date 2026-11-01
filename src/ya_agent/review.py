def build_review_prompt(ticket_text: str, manual_text:str) -> str:
    """把客户工单和本次指定的资料组织成模型请求"""

    # 标出两种输入的来源，避免把客户描述当成产品资料
    return (
        "请生成供售后人员审核的工单处理结果。"
        "产品事实和操作要求只能来自【指定资料】；"
        "findings 中的 evidence.quote 必须逐字引用【指定资料】。"
        "依据不足的事项写为未知，不承诺尚未执行的动作。\n\n"
        f"【客户工单】\n{ticket_text}\n\n"
        f"【指定资料】\n{manual_text}"
    )


