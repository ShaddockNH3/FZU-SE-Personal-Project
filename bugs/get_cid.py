"""据 BV 号查 cid。

逻辑在 bili/ 包里，这个文件只是保留原来的运行方式。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bili import config, crawler, storage


def main():
    bvs = storage.read_json(config.BV_LIST_FILE, []) or []
    if not bvs:
        print(f"{config.BV_LIST_FILE} 是空的，先跑 get_bv.py")
        return 1

    results = crawler.collect_cids(bvs)
    storage.write_json(config.CID_LIST_FILE, results, indent=4)

    ok = sum(1 for item in results.values() if item.get("status") == "success")
    print(f"成功 {ok} 个，失败 {len(results) - ok} 个")
    print(f"结果已写入 {config.CID_LIST_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
