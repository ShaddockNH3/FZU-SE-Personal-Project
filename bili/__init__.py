"""B 站弹幕采集与分析。

流程：抓 BV 号 → 查 cid → 拉弹幕 → 统计导出 Excel → 出词云。

命令行：
    python -m bili bvs|cids|danmaku|analyze|cloud|all

各个 `bugs/` `json/` `cloud/` 下的老脚本仍然能直接跑，它们只是这里的薄包装。
"""

__all__ = ["config", "storage", "parsing", "statistics", "report", "crawler", "danmaku_api", "wordcloud_job"]
