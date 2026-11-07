"""JSON 读写。三个脚本原来各写一遍 open/dump，编码和缩进还不一致。"""

import json
from pathlib import Path
from typing import Any


def read_json(path: Path, default: Any = None) -> Any:
    """文件不存在或解析失败时返回 default，不让流程中断。"""
    file_path = Path(path)
    if not file_path.exists():
        return default
    with file_path.open("r", encoding="utf-8") as handle:
        try:
            return json.load(handle)
        except json.JSONDecodeError:
            return default


def write_json(path: Path, data: Any, indent: int = 2) -> Path:
    """先写临时文件再替换，抓取过程中断电不会留下半个 JSON。"""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = file_path.with_name(file_path.name + ".tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=indent)
    temp_path.replace(file_path)
    return file_path
