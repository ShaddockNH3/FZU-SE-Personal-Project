"""拉弹幕：请求 list.so，解压（B站这批接口是 raw deflate），交给解析层。"""

import zlib

from . import config
from .parsing import Danmaku, parse_danmaku_xml


class RateLimited(RuntimeError):
    """被风控了，调用方应该退避重试。"""


class FetchFailed(RuntimeError):
    """网络错误或拿到的不是弹幕 XML。"""


def decode_body(raw: bytes) -> str:
    """先按 raw deflate 解，不行就当明文。"""
    try:
        return zlib.decompress(raw, -zlib.MAX_WBITS).decode("utf-8")
    except zlib.error:
        return raw.decode("utf-8", errors="ignore")


def fetch_danmaku(cid: str, timeout: int = 10) -> list[Danmaku]:
    """取一个 cid 的弹幕。风控抛 RateLimited，其余失败抛 FetchFailed。"""
    import requests  # pylint: disable=import-outside-toplevel

    try:
        response = requests.get(
            config.DANMAKU_API_URL,
            params={"oid": cid},
            headers={
                "User-Agent": config.BROWSER_HEADERS["User-Agent"],
                "Accept-Encoding": "gzip, deflate",
            },
            timeout=timeout,
        )
    except requests.exceptions.RequestException as error:  # type: ignore[attr-defined]
        raise FetchFailed(str(error)) from error

    if response.status_code == 412:
        raise RateLimited(f"cid {cid} 被风控")

    if response.status_code != 200:
        raise FetchFailed(f"HTTP {response.status_code}")

    text = decode_body(response.content)
    if not text:
        raise FetchFailed("响应为空")

    try:
        return parse_danmaku_xml(text)
    except Exception as error:  # noqa: BLE001 - XML 解析失败统一当拿不到
        raise FetchFailed(f"XML 解析失败: {error}") from error
