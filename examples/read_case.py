from pathlib import Path

# 找到与本脚本放在同一目录的虚构工单文件，路径保存在case_path
# Path是python的一个标准库的一个类，用来表示和操作文件路径
#
case_path = Path(__file__).with_name("x100_case.md")

# 读取文本，确认后续处理流程能拿到完整输入，保存在case_text
case_text = case_path.read_text(encoding="utf-8")


ticket_text,manual_text = case_text.split("# 虚构产品手册摘录", maxsplit=1)



print("__file__",__file__)
print("文档路径：",case_path)
print("完整文档：", case_text)
print("工单部分：", ticket_text)
print("资料部分：", manual_text)