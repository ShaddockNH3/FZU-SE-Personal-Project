"""抓取层：Selenium 翻搜索页拿 BV 号，requests 拿 cid。

两个重依赖都在函数内部 import，所以解析与统计的单测不需要装 selenium/requests。
"""

import re
import time

from . import config
from .parsing import extract_bv, extract_cid


def collect_bvs(keyword: str, target: int = config.TARGET_BV_COUNT) -> list[str]:
    """按关键词翻页抓 BV 号，够 target 个或翻不动就停。"""
    from selenium import webdriver  # pylint: disable=import-outside-toplevel
    from selenium.webdriver.chrome.service import Service as ChromeService  # noqa: E501
    from selenium.webdriver.common.by import By  # pylint: disable=import-outside-toplevel
    from selenium.webdriver.support import expected_conditions as EC  # noqa: E501
    from selenium.webdriver.support.ui import WebDriverWait  # pylint: disable=import-outside-toplevel
    from selenium.common.exceptions import (  # pylint: disable=import-outside-toplevel
        NoSuchElementException,
        TimeoutException,
    )
    from webdriver_manager.chrome import ChromeDriverManager  # pylint: disable=import-outside-toplevel

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    found: list[str] = []

    try:
        driver.get(f"{config.SEARCH_URL}?keyword={keyword}&from_source=webtop_search")
        page = 1

        while len(found) < target:
            print(f"--- 第 {page} 页 ---")
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/video/BV')]"))
                )
            except TimeoutException:
                print("页面加载超时或没有视频，收工")
                break

            for link in driver.find_elements(By.XPATH, "//a[contains(@href, '/video/BV')]"):
                bv = extract_bv(link.get_attribute("href") or "")
                if bv and bv not in found:
                    found.append(bv)

            print(f"累计 {len(found)} / {target}")
            if len(found) >= target:
                break

            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='下一页']"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                time.sleep(0.5)
                next_button.click()
                page += 1
                time.sleep(config.PAGE_TURN_WAIT)
            except (TimeoutException, NoSuchElementException):
                print("没有下一页按钮，收工")
                break
    finally:
        driver.quit()

    return found[:target]


class CidFetchError(RuntimeError):
    """拿不到 cid。"""


def fetch_cid(bv: str, timeout: int = 10) -> str:
    """请求视频页，从 HTML 里抠 cid。"""
    import requests  # pylint: disable=import-outside-toplevel

    url = config.VIDEO_URL.format(bv=bv)
    response = requests.get(url, headers=config.BROWSER_HEADERS, timeout=timeout)
    if response.status_code != 200:
        raise CidFetchError(f"HTTP {response.status_code}")

    cid = extract_cid(response.text)
    if not cid:
        raise CidFetchError("页面里没找到 cid")
    return cid


def collect_cids(bv_list: list[str], gap: float = config.CID_REQUEST_GAP) -> dict:
    """逐个查 cid，结果按 BV 号归档，失败的留错误信息。"""
    results: dict[str, dict] = {}

    for index, bv in enumerate(bv_list, start=1):
        try:
            cid = fetch_cid(bv)
            results[bv] = {"cid": cid, "status": "success"}
            print(f"[{index}/{len(bv_list)}] {bv} -> {cid}")
        except Exception as error:  # noqa: BLE001 - 单个视频失败不该中断整批
            results[bv] = {"error": str(error), "status": "failed"}
            print(f"[{index}/{len(bv_list)}] {bv} 失败: {error}")

        if index < len(bv_list):
            time.sleep(gap)

    return results


def bv_from_text(text: str) -> str:
    """兼容旧接口：从任意文本里抠 BV 号。"""
    matched = re.search(r"(BV[a-zA-Z0-9]{10})", text or "")
    return matched.group(1) if matched else ""
