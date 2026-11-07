"""据 cid 拉弹幕，边抓边存，断了能续。

逻辑在 bili/ 包里，这个文件只是保留原来的运行方式。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bili.cli import run_fetch_danmaku


def main():
    payload = run_fetch_danmaku()
    print(f"共记录 {len(payload)} 个视频")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
