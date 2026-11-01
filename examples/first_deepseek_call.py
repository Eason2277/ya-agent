"""用 Ya Agent 自己的本地配置发起一次最小 DeepSeek 模型调用。"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from ya_agent.schemas import Finding, TicketReview
from ya_agent.evidence import verify_quotes





def main() -> None:
    # __file__ 是当前脚本路径；向上两级找到项目根目录，避免依赖终端所在目录。
    project_root = Path(__file__).resolve().parents[1]

    # 将本项目 .env 中的变量载入当前进程
    load_dotenv(project_root / ".env")

    # 缺少密钥时立即说明原因，避免把后续认证错误误认为模型问题。
    if not os.getenv("DEEPSEEK_API_KEY"):
        raise RuntimeError("请在项目根目录的 .env 中设置 DEEPSEEK_API_KEY")

    # 创建模型对象本身不会发请求，invoke 才会调用 DeepSeek API。
    model = ChatDeepSeek(model="deepseek-chat", max_tokens=1024)
    # 每次运行都重新读取虚构样本；文件改动会影响本次模型输入。
    case_text = (project_root / "examples" / "x100_case.md").read_text(encoding="utf-8")

    # split得到[工单部分，手册部分]; [1]取手册部分供引文核对
    manual_text = case_text.split("# 虚构产品手册摘录", maxsplit=1)[1]

    # 前三段文字规定任务和证据边界，最后用 f 字符串附上实际样本内容。
    prompt = (
        "根据下面的虚构工单和手册摘录，生成一份供售后人员审核的工单处理结果。"
        "findings 中只写手册直接支持的事实，每条 evidence.quote 必须逐字引用手册。"
        "无法确定的具体故障原因放入 unknowns，不要编造维修步骤、保修判断或处理时限。"
        "客户回复和建议下一步只能使用工单已知事实及手册明确写出的要求；"
        "不要添加手册未写明的断电、拆卸或检查指令。"
        "不得声称已经记录工单、安排人员或完成其他尚未执行的动作；"
        "unknowns 不要列举资料没有支持的可能故障原因。"
        "需要授权服务人员进一步评估时，在 escalation 中说明原因。"
        "reply_draft.text 是尚未发送的客户回复；review_note 是给售后人员的审核提醒。\n\n"
        f"{case_text}"
    )

    # 把完整提示词发给模型，返回的 reply 是模型消息；content 是回复正文。
    # reply = model.invoke(prompt)
    # print(reply.content)

    # 要求模型按Finding返回，并将结果解析为Finding对象
    # structured_model = model.with_structured_output(Finding)
    # finding = structured_model.invoke(prompt)

    # 模型提出引文后，由我们自己的代码核对它
    # verify_quotes(finding, manual_text)

    # print(finding.model_dump())

    # 模型按TicketReview填写整份工单处理结果
    structured_model = model.with_structured_output(TicketReview)
    review = structured_model.invoke(prompt)

    # review.findings 是结论列表，每条结论的引文都要核对
    try:
        for finding in review.findings:
            verify_quotes(finding, manual_text)
    except ValueError as error:
        print(f"证据核对失败，结果需要人工检查：{error}")
        return

    print(review.model_dump())


if __name__ == "__main__":
    main()
