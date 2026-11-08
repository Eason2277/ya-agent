import unittest

from ya_agent.evidence import verify_quotes
from ya_agent.schemas import Evidence, Finding


MANUAL_TEXT = "E18 表示传感器信号异常。出现该代码时停止运行，并联系授权服务人员。"


class EvidenceBoundaryTests(unittest.TestCase):
    def test_customer_quote_cannot_be_used_as_manual_quote(self) -> None:
        # 客户报告里的原话不能冒充指定手册中的引文。
        finding = Finding(
            statement="客户报告设备停机",
            kind="fact",
            evidence=[
                Evidence(
                    source_name="客户工单",
                    quote="设备运行时显示 E18，随后停机。",
                )
            ],
        )

        with self.assertRaisesRegex(ValueError, "模型给出的引文不在指定资料中"):
            verify_quotes(finding, MANUAL_TEXT)

    def test_manual_quote_is_accepted(self) -> None:
        # 对照样本：手册中的逐字引文应通过当前的最低限度检查。
        finding = Finding(
            statement="E18 表示传感器信号异常",
            kind="fact",
            evidence=[
                Evidence(
                    source_name="《X100 使用手册》第 8 节",
                    quote="E18 表示传感器信号异常。",
                )
            ],
        )

        self.assertIsNone(verify_quotes(finding, MANUAL_TEXT))


if __name__ == "__main__":
    unittest.main()
