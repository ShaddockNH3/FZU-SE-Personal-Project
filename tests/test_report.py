"""Excel 行数据构造的单测。build_rows 不 import pandas，所以能直接测。"""

import unittest

from bili.report import build_rows
from bili.statistics import analyse


def fake_tokenizer(text):
    return text.split(" ")


class BuildRowsTest(unittest.TestCase):
    def setUp(self):
        payload = {
            "BV1": {
                "danmaku_list": [
                    {"content": "模型 很强", "attributes": "1,1,25,0,0,0,a,1"},
                    {"content": "模型 很强", "attributes": "1,1,25,0,0,0,a,1"},
                    {"content": "前排 围观", "attributes": "2,5,25,0,0,0,b,1"},
                ]
            }
        }
        self.rows = build_rows(analyse(payload, tokenizer=fake_tokenizer))

    def test_totals_sorted_by_count(self):
        totals = self.rows["totals"]
        self.assertEqual(totals[0]["弹幕类型ID"], "1")
        self.assertEqual(totals[0]["类型名称"], "普通滚动")
        self.assertEqual(totals[0]["总数量"], 2)

    def test_sentence_rows_carry_rank(self):
        sentences = self.rows["sentences"]
        self.assertEqual(sentences[0]["排名"], 1)
        self.assertEqual(sentences[0]["弹幕内容(整句)"], "模型 很强")
        self.assertEqual(sentences[0]["出现次数"], 2)

    def test_word_rows_exclude_stopwords(self):
        words = {row["高频词(分词)"] for row in self.rows["words"]}
        self.assertIn("模型", words)
        self.assertNotIn("的", words)

    def test_limit_applies(self):
        rows = build_rows(analyse({"BV": {"danmaku_list": [
            {"content": f"词{i}", "attributes": "1,1,25,0,0,0,a,1"} for i in range(20)
        ]}}, tokenizer=fake_tokenizer), limit=3)
        self.assertLessEqual(len(rows["sentences"]), 3)
        self.assertLessEqual(len(rows["words"]), 3)


if __name__ == "__main__":
    unittest.main()
