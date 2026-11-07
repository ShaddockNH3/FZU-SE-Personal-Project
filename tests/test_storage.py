"""JSON 读写的单测，用临时目录，不碰仓库里的数据文件。"""

import json
import tempfile
import unittest
from pathlib import Path

from bili.storage import read_json, write_json


class StorageTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "data.json"

    def test_round_trip(self):
        payload = {"BV1": {"cid": "1", "list": [1, 2]}}
        write_json(self.path, payload)
        self.assertEqual(read_json(self.path), payload)

    def test_creates_parent_directory(self):
        nested = Path(self.directory.name) / "a" / "b" / "data.json"
        write_json(nested, [1, 2, 3])
        self.assertTrue(nested.exists())

    def test_missing_file_returns_default(self):
        self.assertIsNone(read_json(self.path))
        self.assertEqual(read_json(self.path, {}), {})

    def test_broken_json_returns_default(self):
        self.path.write_text("{not json", encoding="utf-8")
        self.assertEqual(read_json(self.path, {}), {})

    def test_no_temp_file_left_behind(self):
        write_json(self.path, {"a": 1})
        leftovers = list(Path(self.directory.name).glob("*.tmp"))
        self.assertEqual(leftovers, [])

    def test_writes_utf8_without_escaping(self):
        write_json(self.path, {"名字": "弹幕"})
        raw = self.path.read_text(encoding="utf-8")
        self.assertIn("弹幕", raw)
        self.assertEqual(json.loads(raw)["名字"], "弹幕")


if __name__ == "__main__":
    unittest.main()
