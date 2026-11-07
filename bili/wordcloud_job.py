"""词云渲染。jieba / wordcloud / matplotlib 都在函数里 import。"""

from pathlib import Path

from .config import STOP_WORDS, WORDCLOUD_FILE
from .statistics import iter_danmaku


def collect_text(payload: dict) -> str:
    """把所有弹幕内容拼成一段文本。"""
    return " ".join(
        str(danmaku.get("content") or "")
        for _bv, danmaku in iter_danmaku(payload)
        if danmaku.get("content")
    )


def generate(payload: dict, output: Path = WORDCLOUD_FILE, mask_path: Path | None = None) -> Path:
    """生成词云图并保存，返回文件路径。"""
    import jieba  # pylint: disable=import-outside-toplevel
    import matplotlib.pyplot as plt  # pylint: disable=import-outside-toplevel
    import numpy as np  # pylint: disable=import-outside-toplevel
    from PIL import Image  # pylint: disable=import-outside-toplevel
    from wordcloud import WordCloud  # pylint: disable=import-outside-toplevel

    text = collect_text(payload)
    if not text.strip():
        raise ValueError("没有弹幕内容，做不了词云")

    words = " ".join(
        word for word in jieba.cut(text)
        if word.strip() and word not in STOP_WORDS and not word.isnumeric()
    )

    mask = None
    if mask_path and Path(mask_path).exists():
        mask = np.array(Image.open(mask_path))

    cloud = WordCloud(
        font_path=_find_cjk_font(),
        width=1200,
        height=800,
        background_color="white",
        stopwords=set(STOP_WORDS),
        mask=mask,
        collocations=False,
    ).generate(words)

    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(12, 8))
    plt.imshow(cloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(target, dpi=200, bbox_inches="tight")
    plt.close()
    return target


def _find_cjk_font() -> str:
    """挑一个能显示中文的字体，找不到就让 wordcloud 用默认（会变方块）。"""
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "C:/Windows/Fonts/msyh.ttc",
    ]
    for path in candidates:
        if Path(path).exists():
            return path
    return ""
