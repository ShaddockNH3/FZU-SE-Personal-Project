"""统一的配置：关键词、目标数量、路径、接口地址、弹幕类型与停用词。"""

from pathlib import Path

# 抓取目标
KEYWORD = "LLM"
TARGET_BV_COUNT = 360

# 目录约定：脚本默认从仓库根目录运行
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "json"
XLSX_DIR = ROOT / "xlsx"
CLOUD_DIR = ROOT / "cloud"

BV_LIST_FILE = DATA_DIR / f"{KEYWORD}_bv_list.json"
CID_LIST_FILE = DATA_DIR / f"{KEYWORD}_cid_list.json"
DANMAKU_FILE = DATA_DIR / f"{KEYWORD}_danmaku_realtime_save.json"
EXCEL_FILE = XLSX_DIR / f"{KEYWORD}_danmaku_statistics.xlsx"
WORDCLOUD_FILE = CLOUD_DIR / f"{KEYWORD}_danmaku_wordcloud_beautiful.png"

# 接口
SEARCH_URL = "https://search.bilibili.com/all"
VIDEO_URL = "https://www.bilibili.com/video/{bv}"
DANMAKU_API_URL = "https://api.bilibili.com/x/v1/dm/list.so"
BROWSER_HEADERS = {"User-Agent": "Mozilla/5.0"}

# 节流（秒）
PAGE_TURN_WAIT = 3
CID_REQUEST_GAP = 1
DANMAKU_GAP_RANGE = (10, 20)
RATE_LIMIT_BACKOFF = 120

# 弹幕类型：属性串第二段是模式编号
MODE_MAP = {
    "1": "普通滚动", "2": "普通滚动", "3": "普通滚动",
    "4": "底部弹幕", "5": "顶部弹幕", "6": "逆向弹幕",
    "7": "高级弹幕", "8": "代码弹幕", "9": "BAS弹幕",
}

TOP_N = 8


def mode_name(mode: str) -> str:
    """模式编号转中文名，认不出来就标未知。"""
    return MODE_MAP.get(mode, f"未知类型({mode})")


# 停用词：原来 json/deal_json.py 和 cloud/cloud.py 各存一份且略有出入，
# 这里取并集，两个流程用同一套，免得词云和图表的停用标准不一致。
STOP_WORDS = frozenset({
    # 基础虚词
    "的", "是", "了", "在", "也", "啊", "吗", "吧", "呢", "哦", "哈", "哈哈", "哈哈哈", "啊啊啊",
    "这", "那", "就", "都", "不", "我", "你", "他", "她", "它", "们", "个", "一", "有", "人",
    "什么", "怎么", "为", "于", "上", "下", "左", "右", "前", "后", "里", "外", "还",
    "地", "得", "和", "与", "或", "被", "把", "但", "所以", "因为", "不过", "自己", "没有",
    "真的", "还是", "就是", "不是", "可以", "这个是", "为什么", "卧槽", "草", "nb", "respect", "多",
    # 符号
    "\\", "-", "^", "_", "~", '"', "/", ",", ":", "`", "*", "&", "%", "$", "#", "@",
    "，", "。", "！", "？", "：", "；", "（", "）", "[", "]", "【", "】", " ",
    ".", "!", "?", "(", ")",
    "...", "....", ".....", "......", "→", "←", "…", "·", "《", "》",
    # 无信息量的口语与套话
    "大", "很", "不错", "精彩", "讲", "又", "所有", "基本", "作用", "很大",
    "好", "看", "来", "开始", "现在", "收藏", "老师", "学习", "游戏",
    "test", "up", "三连", "万物", "之源", "逆行", "一号",
    "up主", "UP主", "UP", "阿婆主", "视频", "弹幕", "感谢", "主播", "直播", "直播间",
    "来了", "来了来了", "233", "2333", "666", "6666", "666666",
    "一个", "这个", "那个", "这里", "那里", "但是", "然而", "如果", "我们",
    "感觉", "觉得", "问题", "一样", "说", "没", "能", "做", "去", "想", "要",
    "一点", "一些", "一种", "有点", "东西", "多少", "这么",
    # 英文停用词
    "this", "is", "a", "to", "and", "the", "that", "of", "for", "in", "it", "with", "on", "was", "as",
})
