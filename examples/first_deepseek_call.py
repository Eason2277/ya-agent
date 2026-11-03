"""用 Ya Agent 自己的本地配置发起一次最小 DeepSeek 模型调用。"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek

from ya_agent.core.review_ticket import review_ticket, TicketReviewParseError
from ya_agent.schemas import Finding, TicketReview
from ya_agent.evidence import verify_quotes, verify_review_quotes
from ya_agent.review import build_review_prompt





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
    # split，对指定的字符串内容进行切割
    ticket_text, manual_text = case_text.split("# 虚构产品手册摘录", maxsplit=1)

    # 核心函数接收本次工单，指定资料和模型；成功后返回待人工审核的结果
    try:
        review = review_ticket(ticket_text, manual_text, model)
    except TicketReviewParseError as error:
        # 入口只显示安全的简短原因，原始回复保存在一场对象中供排查
        print(f"结构化解析失败，需要人工检查：{error}")
        return
    except ValueError as error:
        # 核心的引文核对对失败会以ValueError传到这里
        print(f"证据核对失败，需要人工检查：{error}")
        return

    print(review.model_dump())


if __name__ == "__main__":
    main()
