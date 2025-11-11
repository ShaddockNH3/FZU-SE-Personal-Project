import time
import re
import json  # 引入 json 模块用于数据序列化
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def get_bilibili_bvs(keyword, max_bvs=360):
    """抓取B站搜索结果的BV号"""
    try:
        print("正在自动检查和下载匹配的 ChromeDriver...")
        driver = webdriver.Chrome(
            service=ChromeService(
                ChromeDriverManager().install()))
        print("ChromeDriver 初始化成功")

    except Exception as e:
        print("浏览器启动失败")
        print(f"可能原因：网络问题或 ChromeDriver 自动下载失败。错误信息: {e}")
        return []

    start_url = f"https://search.bilibili.com/all?keyword={keyword}&from_source=webtop_search"
    driver.get(start_url)

    bv_set = set()
    current_page = 1

    try:
        while len(bv_set) < max_bvs:
            print(f"\n--- 正在抓取第 {current_page} 页 ---")

            try:
                WebDriverWait(
                    driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//a[contains(@href, '/video/BV')]")))
            except TimeoutException:
                print("页面加载超时，或当前页面无视频内容")
                break

            video_links = driver.find_elements(
                By.XPATH, "//a[contains(@href, '/video/BV')]")
            found_count_this_page = 0

            for link in video_links:
                href = link.get_attribute('href')
                if not href:
                    continue
                match = re.search(r'(BV[a-zA-Z0-9]{10})', href)
                if match:
                    bv_id = match.group(1)
                    if bv_id not in bv_set:
                        bv_set.add(bv_id)
                        found_count_this_page += 1

            print(f"当前页发现 {found_count_this_page} 个新的 BV 号")
            print(f"累计收集: {len(bv_set)} / {max_bvs} 个 BV 号")

            if len(bv_set) >= max_bvs:
                print(f"已达到目标数量 {max_bvs}，数据采集完成")
                break

            try:
                print("正在滚动到页面底部以加载分页按钮...")
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

                next_button_locator = (By.XPATH, "//button[text()='下一页']")

                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(next_button_locator)
                )

                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", next_button)
                time.sleep(0.5)

                next_button.click()
                current_page += 1
                time.sleep(3)

            except (TimeoutException, NoSuchElementException):
                print("未找到\"下一页\"按钮，已到达最后一页")
                break

    except Exception as e:
        print(f"数据抓取过程中发生错误: {e}")
    finally:
        driver.quit()
        print("浏览器已关闭")

    return list(bv_set)[:max_bvs]


def save_to_json(bv_list, filename="bilibili_bvs.json"):
    """保存BV号列表到JSON文件"""
    if not bv_list:
        print("列表为空，无数据可保存")
        return

    print(f"\n正在保存 {len(bv_list)} 个 BV 号到 {filename} ...")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(bv_list, f, indent=4, ensure_ascii=False)

        print(f"数据保存成功，文件路径: {filename}")
    except Exception as e:
        print(f"JSON 文件保存失败。错误信息: {e}")


if __name__ == "__main__":
    KEYWORD_TO_SEARCH = "LLM"
    TARGET_COUNT = 360

    print(f"开始数据采集任务... 关键词: '{KEYWORD_TO_SEARCH}', 目标数量: {TARGET_COUNT}")
    all_bvs = get_bilibili_bvs(KEYWORD_TO_SEARCH, TARGET_COUNT)

    if all_bvs:
        save_to_json(
            all_bvs,
            filename=f"json/{KEYWORD_TO_SEARCH}_bv_list.json")
