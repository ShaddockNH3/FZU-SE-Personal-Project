"""文本解析：BV 号、cid、弹幕 XML。全是纯函数，不碰网络和文件。"""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from .config import mode_name

BV_PATTERN = re.compile(r"(BV[a-zA-Z0-9]{10})")
CID_PATTERN = re.compile(r'"cid":(\d+)')


def extract_bv(href: str) -> str:
    """从链接里挑出 BV 号，挑不到返回空串。"""
    matched = BV_PATTERN.search(href or "")
    return matched.group(1) if matched else ""


def extract_cid(html: str) -> str:
    """视频页 HTML 里第一个 "cid":数字 就是正片 cid。"""
    matched = CID_PATTERN.search(html or "")
    return matched.group(1) if matched else ""


@dataclass(frozen=True)
class Danmaku:
    """一条弹幕：内容 + 原始属性串（p 属性，逗号分隔）。"""

    content: str
    attributes: str

    @property
    def mode(self) -> str:
        """属性串第二段是弹幕模式编号。"""
        parts = self.attributes.split(",")
        return parts[1] if len(parts) > 1 else ""

    @property
    def mode_name(self) -> str:
        return mode_name(self.mode)


def parse_danmaku_xml(xml_text: str) -> list[Danmaku]:
    """解析弹幕 XML。根节点不是 <i> 就当没有弹幕，而不是抛异常。"""
    if not xml_text:
        return []
    root = ET.fromstring(xml_text)
    if root.tag != "i":
        return []
    return [
        Danmaku(content=element.text or "", attributes=element.get("p") or "")
        for element in root.findall("d")
    ]
