"""抓关键词的 BV 号列表。

逻辑在 bili/ 包里，这个文件只是保留原来的运行方式。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bili import config, crawler, storage


def main():
    print(f"开始抓取，关键词：{config.KEYWORD}，目标 {config.TARGET_BV_COUNT} 个")
    bvs = crawler.collect_bvs(config.KEYWORD, config.TARGET_BV_COUNT)
    if not bvs:
        print("一个都没抓到，检查网络或选择器")
        return 1
    storage.write_json(config.BV_LIST_FILE, bvs, indent=4)
    print(f"已写入 {config.BV_LIST_FILE}，共 {len(bvs)} 个")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
