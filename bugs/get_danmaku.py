import requests
import json
import os
import time
import random
import zlib
import xml.etree.ElementTree as ET

DANMAKU_API_URL = 'https://api.bilibili.com/x/v1/dm/list.so'
HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/108.0.0.0 Safari/537.36'),
    'Accept-Encoding': 'gzip, deflate',
}


def fetch_danmaku_xml(cid):
    """抓取指定cid的弹幕数据"""
    params = {'oid': cid}
    print(f"  > 正在请求 cid: {cid} 的弹幕...")

    try:
        resp = requests.get(
            DANMAKU_API_URL,
            params=params,
            headers=HEADERS,
            timeout=10)

        if resp.status_code == 412:
            print("  > 检测到B站风控系统响应412状态码")
            return "RATE_LIMIT"

        resp.raise_for_status()

        xml_content = None
        try:
            decompressed_data = zlib.decompress(resp.content, -zlib.MAX_WBITS)
            xml_content = decompressed_data.decode('utf-8')
        except zlib.error:
            xml_content = resp.content.decode('utf-8', errors='ignore')

        if xml_content:
            try:
                root = ET.fromstring(xml_content)
                danmaku_list = []
                if root.tag != 'i':
                    return None
                for d_element in root.findall('d'):
                    danmaku_list.append(
                        {'content': d_element.text, 'attributes': d_element.get('p')})
                return danmaku_list
            except ET.ParseError:
                return None
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"  > 网络请求错误: 抓取 cid: {cid} 失败 - {e}")
        return None


if __name__ == "__main__":
    cid_list_file = 'json/LLM_cid_list.json'
    output_filename = 'json/LLM_danmaku_realtime_save.json'
    all_videos_danmaku = {}

    if os.path.exists(output_filename):
        with open(output_filename, 'r', encoding='utf-8') as f:
            try:
                all_videos_danmaku = json.load(f)
            except BaseException:
                pass
    if not os.path.exists(cid_list_file):
        exit(f"错误: 找不到输入文件 '{cid_list_file}'")
    with open(cid_list_file, 'r', encoding='utf-8') as f:
        cid_data = json.load(f)

    print(f"开始处理任务: 共 {len(cid_data)} 个视频需要抓取弹幕")

    video_keys = list(cid_data.keys())
    i = 0
    while i < len(video_keys):
        bv = video_keys[i]
        info = cid_data[bv]

        if bv in all_videos_danmaku:
            i += 1
            continue

        cid = info.get('cid')
        if not (info.get('status') == 'success' and cid):
            i += 1
            continue

        print(f"\n--- 正在准备处理视频 {bv} ---")

        sleep_duration = random.uniform(10, 20)
        print(f"   等待 {sleep_duration:.2f} 秒后发起请求...")
        time.sleep(sleep_duration)

        danmaku_list = fetch_danmaku_xml(cid)

        if danmaku_list == "RATE_LIMIT":
            long_break_time = 120
            print(f"  > 触发频率限制，等待 {long_break_time} 秒后重试...")
            time.sleep(long_break_time)
            print("  > 等待结束，重新尝试当前视频...")
            continue

        if danmaku_list is not None:
            print(f"  > 成功！为 {bv} 抓到了 {len(danmaku_list)} 条弹幕！")
            all_videos_danmaku[bv] = {
                'cid': cid,
                'danmaku_count': len(danmaku_list),
                'danmaku_list': danmaku_list}
        else:
            print(f"  > 失败或无弹幕！暂时跳过 {bv}。")
            all_videos_danmaku[bv] = {
                'cid': cid, 'status': 'fetch_failed_or_no_danmaku'}

        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(all_videos_danmaku, f, ensure_ascii=False, indent=2)
            print(
                f"  > 进度已保存 (当前进度: {len(all_videos_danmaku)}/{len(cid_data)} 条记录)")
        except Exception as e:
            print(f"  > 保存进度失败: {e}")

        i += 1

    print("\n\n任务完成: 所有视频的弹幕抓取已处理完毕")
