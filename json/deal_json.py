"""统计弹幕并导出 Excel。

逻辑在 bili/ 包里，这个文件只是保留原来的运行方式。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bili import statistics, storage, config, report


def main():
    payload = storage.read_json(config.DANMAKU_FILE, {}) or {}
    if not payload:
        print(f"{config.DANMAKU_FILE} 是空的，先跑 get_danmaku.py")
        return 1

    analysis = statistics.analyse(payload)
    print(f"处理了 {analysis.processed} 条弹幕")

    path = report.write_excel(analysis)
    print(f"报告已写入 {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
