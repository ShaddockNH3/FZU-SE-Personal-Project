"""解析层的单测。只依赖标准库，不需要 selenium / requests / pandas。"""

import unittest

from bili.parsing import Danmaku, extract_bv, extract_cid, parse_danmaku_xml


class ExtractBvTest(unittest.TestCase):
    def test_picks_bv_from_search_href(self):
        href = "https://www.bilibili.com/video/BV1xx411c7mD?spm_id_from=333.337"
        self.assertEqual(extract_bv(href), "BV1xx411c7mD")

    def test_returns_empty_when_missing(self):
        self.assertEqual(extract_bv("https://www.bilibili.com/read/cv123"), "")
        self.assertEqual(extract_bv(""), "")
        self.assertEqual(extract_bv(None), "")


class ExtractCidTest(unittest.TestCase):
    def test_reads_first_cid_in_page(self):
        html = '{"code":0,"data":{"cid":123456789,"aid":1}}'
        self.assertEqual(extract_cid(html), "123456789")

    def test_returns_empty_when_missing(self):
        self.assertEqual(extract_cid("<html></html>"), "")


class ParseDanmakuXmlTest(unittest.TestCase):
    XML = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<i><chatserver>chat.bilibili.com</chatserver>"
        '<d p="1.5,1,25,16777215,1700000000,0,abc,1">第一条</d>'
        '<d p="2.5,5,25,16777215,1700000001,0,def,2">第二条</d>'
        "</i>"
    )

    def test_parses_each_d_element(self):
        items = parse_danmaku_xml(self.XML)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].content, "第一条")
        self.assertEqual(items[1].content, "第二条")

    def test_mode_comes_from_second_attribute(self):
        items = parse_danmaku_xml(self.XML)
        self.assertEqual(items[0].mode, "1")
        self.assertEqual(items[0].mode_name, "普通滚动")
        self.assertEqual(items[1].mode, "5")
        self.assertEqual(items[1].mode_name, "顶部弹幕")

    def test_non_danmaku_root_returns_empty(self):
        self.assertEqual(parse_danmaku_xml("<html><body>412</body></html>"), [])

    def test_empty_input_returns_empty(self):
        self.assertEqual(parse_danmaku_xml(""), [])

    def test_malformed_attributes_do_not_crash(self):
        self.assertEqual(Danmaku("x", "").mode, "")
        self.assertEqual(Danmaku("x", "1.5").mode, "")


if __name__ == "__main__":
    unittest.main()
