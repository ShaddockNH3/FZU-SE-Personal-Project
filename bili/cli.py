"""命令行入口：把五步流程做成子命令，也能一条命令跑完。"""

import argparse
import random
import time

from . import config, crawler, danmaku_api, report, statistics, storage, wordcloud_job


def run_collect_bvs(keyword: str, count: int) -> list[str]:
    bvs = crawler.collect_bvs(keyword, count)
    storage.write_json(config.BV_LIST_FILE, bvs, indent=4)
    print(f"共 {len(bvs)} 个 BV 号，已写入 {config.BV_LIST_FILE}")
    return bvs


def run_collect_cids() -> dict:
    bvs = storage.read_json(config.BV_LIST_FILE, []) or []
    if not bvs:
        raise SystemExit(f"{config.BV_LIST_FILE} 是空的，先跑 bvs")

    results = crawler.collect_cids(bvs)
    storage.write_json(config.CID_LIST_FILE, results, indent=4)
    ok = sum(1 for item in results.values() if item.get("status") == "success")
    print(f"成功 {ok} 个，失败 {len(results) - ok} 个，已写入 {config.CID_LIST_FILE}")
    return results


def run_fetch_danmaku() -> dict:
    cid_data = storage.read_json(config.CID_LIST_FILE, {}) or {}
    if not cid_data:
        raise SystemExit(f"{config.CID_LIST_FILE} 是空的，先跑 cids")

    payload = storage.read_json(config.DANMAKU_FILE, {}) or {}
    todo = [bv for bv in cid_data if bv not in payload]
    print(f"待抓取 {len(todo)} / {len(cid_data)} 个视频")

    for index, bv in enumerate(todo, start=1):
        info = cid_data[bv]
        if info.get("status") != "success" or not info.get("cid"):
            continue

        wait = random.uniform(*config.DANMAKU_GAP_RANGE)
        print(f"[{index}/{len(todo)}] {bv}：先等 {wait:.1f} 秒")
        time.sleep(wait)

        try:
            danmaku = danmaku_api.fetch_danmaku(info["cid"])
        except danmaku_api.RateLimited:
            print(f"被风控，退避 {config.RATE_LIMIT_BACKOFF} 秒后继续")
            time.sleep(config.RATE_LIMIT_BACKOFF)
            continue
        except danmaku_api.FetchFailed as error:
            print(f"{bv} 拿不到弹幕: {error}")
            payload[bv] = {"cid": info["cid"], "status": "fetch_failed_or_no_danmaku"}
            storage.write_json(config.DANMAKU_FILE, payload, indent=2)
            continue

        payload[bv] = {
            "cid": info["cid"],
            "danmaku_count": len(danmaku),
            "danmaku_list": [{"content": item.content, "attributes": item.attributes} for item in danmaku],
        }
        print(f"{bv}：{len(danmaku)} 条")
        storage.write_json(config.DANMAKU_FILE, payload, indent=2)

    return payload


def run_analyze() -> object:
    payload = storage.read_json(config.DANMAKU_FILE, {}) or {}
    if not payload:
        raise SystemExit(f"{config.DANMAKU_FILE} 是空的，先跑 danmaku")

    try:
        analysis = statistics.analyse(payload)
    except ImportError as error:
        raise SystemExit(f"统计要用 jieba：{error}. 先 pip install -r requirements.txt") from error
    print(f"处理了 {analysis.processed} 条弹幕，共 {len(analysis.totals)} 种类型")

    try:
        path = report.write_excel(analysis)
    except ImportError as error:
        raise SystemExit(f"导出 Excel 要用 pandas/openpyxl：{error}. 先 pip install -r requirements.txt") from error
    print(f"报告已写入 {path}")
    return analysis


def run_wordcloud() -> object:
    payload = storage.read_json(config.DANMAKU_FILE, {}) or {}
    if not payload:
        raise SystemExit(f"{config.DANMAKU_FILE} 是空的，先跑 danmaku")

    try:
        path = wordcloud_job.generate(payload)
    except ImportError as error:
        raise SystemExit(f"画词云要用 jieba/wordcloud/matplotlib：{error}. 先 pip install -r requirements.txt") from error
    print(f"词云已写入 {path}")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bili", description="B 站弹幕采集与统计")
    sub = parser.add_subparsers(dest="command", required=True)

    bvs = sub.add_parser("bvs", help="按关键词抓 BV 号")
    bvs.add_argument("--keyword", default=config.KEYWORD)
    bvs.add_argument("--count", type=int, default=config.TARGET_BV_COUNT)

    sub.add_parser("cids", help="据 BV 号查 cid")
    sub.add_parser("danmaku", help="据 cid 拉弹幕，支持断点续跑")
    sub.add_parser("analyze", help="统计并导出 Excel")
    sub.add_parser("cloud", help="生成词云图")
    sub.add_parser("all", help="从抓 BV 号一路跑到词云")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "bvs":
        run_collect_bvs(args.keyword, args.count)
    elif args.command == "cids":
        run_collect_cids()
    elif args.command == "danmaku":
        run_fetch_danmaku()
    elif args.command == "analyze":
        run_analyze()
    elif args.command == "cloud":
        run_wordcloud()
    elif args.command == "all":
        run_collect_bvs(config.KEYWORD, config.TARGET_BV_COUNT)
        run_collect_cids()
        run_fetch_danmaku()
        run_analyze()
        run_wordcloud()

    return 0
