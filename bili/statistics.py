"""弹幕统计：按类型计数、整句排行、分词后词频排行。

分词器做成参数，默认才用 jieba —— 测试里塞一个假的就能跑，不用装依赖。
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Callable, Iterable

from .config import STOP_WORDS, mode_name

Tokenizer = Callable[[str], list[str]]


def jieba_tokenizer(text: str) -> list[str]:
    """默认分词器，只在真正需要时才 import jieba。"""
    import jieba  # pylint: disable=import-outside-toplevel

    return list(jieba.lcut(text))


@dataclass
class Analysis:
    totals: Counter = field(default_factory=Counter)
    sentences: dict = field(default_factory=lambda: defaultdict(Counter))
    words: dict = field(default_factory=lambda: defaultdict(Counter))
    processed: int = 0

    def top_sentences(self, mode: str, limit: int = 8) -> list[tuple[str, int]]:
        return self.sentences[mode].most_common(limit)

    def top_words(self, mode: str, limit: int = 8) -> list[tuple[str, int]]:
        return self.words[mode].most_common(limit)


def keep_word(word: str, stop_words: frozenset[str] = STOP_WORDS) -> bool:
    """过滤空白、停用词和纯数字。"""
    token = word.strip()
    if not token:
        return False
    if token in stop_words:
        return False
    return not token.isnumeric()


def iter_danmaku(payload: dict) -> Iterable[tuple[str, dict]]:
    """遍历一份抓取结果，跳过标记失败或没弹幕的视频。"""
    for bv, video in (payload or {}).items():
        if not isinstance(video, dict):
            continue
        if video.get("status") == "fetch_failed_or_no_danmaku":
            continue
        for danmaku in video.get("danmaku_list") or []:
            yield bv, danmaku


def analyse(
    payload: dict,
    tokenizer: Tokenizer = jieba_tokenizer,
    stop_words: frozenset[str] = STOP_WORDS,
) -> Analysis:
    """一次遍历算三张表：类型总数、整句排行、词频排行。"""
    result = Analysis()

    for _bv, danmaku in iter_danmaku(payload):
        content = danmaku.get("content")
        attributes = danmaku.get("attributes")
        if not attributes or content is None:
            continue

        mode = attributes.split(",")[1] if "," in attributes else ""
        result.totals[mode] += 1
        result.sentences[mode][content] += 1

        tokens = [word for word in tokenizer(str(content).lower()) if keep_word(word, stop_words)]
        result.words[mode].update(tokens)
        result.processed += 1

    return result


def mode_label(mode: str) -> str:
    return mode_name(mode)
