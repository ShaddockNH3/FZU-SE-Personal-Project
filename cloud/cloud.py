"""生成弹幕词云。

逻辑在 bili/ 包里，这个文件只是保留原来的运行方式。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bili import config, storage, wordcloud_job


def main():
    payload = storage.read_json(config.DANMAKU_FILE, {}) or {}
    if not payload:
        print(f"{config.DANMAKU_FILE} 是空的，先跑 get_danmaku.py")
        return 1

    path = wordcloud_job.generate(payload)
    print(f"词云已写入 {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
