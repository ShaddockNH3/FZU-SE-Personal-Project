"""统计层的单测。分词器传假的，所以不需要 jieba。"""

import unittest

from bili.config import STOP_WORDS
from bili.statistics import analyse, iter_danmaku, keep_word


def fake_tokenizer(text):
    """按空格切，够用来验证过滤和计数。"""
    return text.split(" ")


def sample_payload():
    return {
        "BV1": {
            "cid": "1",
            "danmaku_list": [
                {"content": "的 模型 真 强", "attributes": "1.0,1,25,0,0,0,abc,1"},
                {"content": "模型 模型 快", "attributes": "2.0,1,25,0,0,0,def,1"},
                {"content": "123 前排", "attributes": "3.0,5,25,0,0,0,ghi,1"},
            ],
        },
        "BV2": {
            "cid": "2",
            "status": "fetch_failed_or_no_danmaku",
            "danmaku_list": [{"content": "不该被统计", "attributes": "4.0,1,25,0,0,0,jkl,1"}],
        },
    }


class AnalyseTest(unittest.TestCase):
    def setUp(self):
        self.analysis = analyse(sample_payload(), tokenizer=fake_tokenizer)

    def test_counts_by_mode(self):
        self.assertEqual(self.analysis.totals["1"], 2)
        self.assertEqual(self.analysis.totals["5"], 1)

    def test_skips_failed_video(self):
        self.assertEqual(self.analysis.processed, 3)
        self.assertNotIn("不该被统计", str(self.analysis.sentences))

    def test_top_sentences(self):
        top = dict(self.analysis.top_sentences("1"))
        # 两条都只出现一次，不断言先后顺序（Counter 并列时按插入序）
        self.assertEqual(top["模型 模型 快"], 1)
        self.assertEqual(top["的 模型 真 强"], 1)
        self.assertEqual(len(top), 2)

    def test_word_frequency_filters_stopwords_and_numbers(self):
        words = dict(self.analysis.top_words("1"))
        self.assertEqual(words["模型"], 3)
        self.assertNotIn("的", words)
        self.assertNotIn("123", words)

    def test_empty_payload(self):
        empty = analyse({}, tokenizer=fake_tokenizer)
        self.assertEqual(empty.processed, 0)
        self.assertEqual(dict(empty.totals), {})


class KeepWordTest(unittest.TestCase):
    def test_rules(self):
        self.assertTrue(keep_word("模型"))
        self.assertFalse(keep_word("的"))
        self.assertFalse(keep_word("123"))
        self.assertFalse(keep_word("   "))

    def test_custom_stopwords(self):
        self.assertFalse(keep_word("模型", frozenset({"模型"})))
        self.assertTrue(keep_word("模型", STOP_WORDS))


class IterDanmakuTest(unittest.TestCase):
    def test_skips_entries_without_list(self):
        payload = {"BV1": {"status": "success"}, "BV2": {"danmaku_list": [{"content": "a"}]}}
        self.assertEqual(len(list(iter_danmaku(payload))), 1)


if __name__ == "__main__":
    unittest.main()
