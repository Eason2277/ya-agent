from langchain_deepseek import ChatDeepSeek
from ya_agent.evidence import verify_review_quotes
from ya_agent.review import build_review_prompt
from ya_agent.schemas import TicketReview


class TicketReviewParseError(RuntimeError):
    """模型没有生成可用的 TicketReview 时，向调用方交代失败并保留诊断信息。"""

    def __init__(self, raw: object, parsing_error: BaseException | None) -> None:
        # super() 调用 RuntimeError 的初始化逻辑，让 str(error) 得到安全、固定的提示。
        # 原始回复可能含工单内容，因此不拼进默认错误消息。
        super().__init__("模型未返回可解析的工单结果")

        # self 上的属性会随异常对象交给入口层，供授权的排查流程按需读取。
        # parsing_error 可能为 None：解析结果为空不一定伴随解析器异常。
        self.raw = raw
        self.parsing_error = parsing_error

class TicketReviewEvidenceError(ValueError):
    """引文核对失败；保留已解析结果供人工排查"""

    def __init__(self, review: TicketReview) -> None:
        #失败结果只能用于排查，不能作为已通过核对的客户回复

        super().__init__("模型引文未通过指定资料核对")
        self.review = review


def review_ticket(
        ticket_text: str,
        manual_text: str,
        model: ChatDeepSeek
) -> TicketReview:
    """处理入口层传入的一条工单及指定资料，返回待人工审核的 TicketReview。

    示例脚本和未来的 CLI/API 负责准备文本与模型，并接收这里返回的结果。
    解析结果为空时抛 TicketReviewParseError；引文不在资料中时抛
    TicketReviewEvidenceError，并保留已解析的结果供入口层排查。
    """

    # ticket_text 是客户工单，manual_text 是本次允许使用的资料；提示词函数
    # 把两者和证据约束组合起来，结果交给下面的模型调用。
    prompt = build_review_prompt(ticket_text, manual_text)
    # 这里只配置输出结构。include_raw=True 让调用后同时拿到原始回复、
    # 解析后的对象和解析错误，以便区分生成内容与程序核对结果。
    structured_model = model.with_structured_output(TicketReview, include_raw=True)

    # invoke 才向模型发请求。result 是包含 raw、parsed、parsing_error 的字典；
    # parsed 成功时是 TicketReview，失败时可能为 None。
    result = structured_model.invoke(prompt)
    review = result["parsed"]

    # 没有可用的结构化结果时立即结束，避免把空值当作工单结果继续处理。
    # 异常保留 raw 和 parsing_error，具体如何显示由入口层决定。
    if review is None:
        raise TicketReviewParseError(
            raw=result["raw"],
            parsing_error=result["parsing_error"],
        )
    # 逐条核对引文是否出现在指定资料中；底层 ValueError 在此转为
    # 带有已解析结果的 TicketReviewEvidenceError，交给入口层说明失败。
    # 通过后返回 Pydantic 对象，供售后人员在入口界面继续审核和修改。

    try:
        verify_review_quotes(review, manual_text)
    except ValueError as error:
        raise TicketReviewEvidenceError(review) from error


    return review
