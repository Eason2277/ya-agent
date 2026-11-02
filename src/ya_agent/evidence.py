from ya_agent.schemas import Finding, TicketReview


def verify_quotes(finding: Finding,source_text: str) -> None:
    """核对一条结论中的引文是否逐字出现在指定资料中"""

    # Finding 可以包含多条依据，因此逐条检查
    for evidence in finding.evidence:
        # 如果引文为空或者只有空白或者完整引文不是逐字出现在资料文字中
        if not evidence.quote.strip() or evidence.quote not in source_text:
            # 抛出异常
            raise ValueError(f"模型给出的引文不在指定资料中：{evidence.quote!r}")




def verify_review_quotes(review: TicketReview, source_text: str) -> None:
    """核对整份结果的引文；任一引文缺失时将错误交给调用方。"""
    for finding in review.findings:
        verify_quotes(finding, source_text)
