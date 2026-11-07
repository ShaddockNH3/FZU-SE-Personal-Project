"""把统计结果写成 Excel。pandas 只在真要导表时才 import。"""

from pathlib import Path

from .config import EXCEL_FILE, TOP_N, mode_name
from .statistics import Analysis


def build_rows(analysis: Analysis, limit: int = TOP_N) -> dict[str, list[dict]]:
    """把 Analysis 摊成三张表的行数据，和原来的三个 sheet 一一对应。"""
    totals_rows = [
        {"弹幕类型ID": mode, "类型名称": mode_name(mode), "总数量": count}
        for mode, count in analysis.totals.most_common()
    ]

    sentence_rows = []
    for mode, counter in analysis.sentences.items():
        for rank, (content, freq) in enumerate(counter.most_common(limit), start=1):
            sentence_rows.append({
                "弹幕类型ID": mode,
                "类型名称": mode_name(mode),
                "排名": rank,
                "弹幕内容(整句)": content,
                "出现次数": freq,
            })

    word_rows = []
    for mode, counter in analysis.words.items():
        for rank, (word, freq) in enumerate(counter.most_common(limit), start=1):
            word_rows.append({
                "弹幕类型ID": mode,
                "类型名称": mode_name(mode),
                "排名": rank,
                "高频词(分词)": word,
                "出现次数": freq,
            })

    return {
        "totals": totals_rows,
        "sentences": sentence_rows,
        "words": word_rows,
    }


def write_excel(analysis: Analysis, path: Path = EXCEL_FILE) -> Path:
    """三个 sheet：类型总览、热门整句、热门词频。"""
    import pandas as pd  # pylint: disable=import-outside-toplevel

    rows = build_rows(analysis)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(target, engine="openpyxl") as writer:
        pd.DataFrame(rows["totals"]).to_excel(writer, sheet_name="弹幕类型总览", index=False)
        pd.DataFrame(rows["sentences"]).to_excel(writer, sheet_name="热门弹幕(整句)Top8", index=False)
        pd.DataFrame(rows["words"]).to_excel(writer, sheet_name="热门词频(分词)Top8", index=False)

    return target
