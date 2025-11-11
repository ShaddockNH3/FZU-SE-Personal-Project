import requests
import re

import json
import time


def get_cid(video_url):
    """获取视频的cid"""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(video_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch video page: {response.status_code}")

    match = re.search(r'"cid":(\d+)', response.text)
    if match:
        return match.group(1)
    else:
        raise Exception("Failed to find cid in video page")


if __name__ == "__main__":

    with open('json/LLM_bv_list.json', 'r', encoding='utf-8') as f:
        bv_list = json.load(f)

    results = {}

    for index, bv_id in enumerate(bv_list, 1):
        video_url = f"https://www.bilibili.com/video/{bv_id}"
        try:
            cid = get_cid(video_url)
            results[bv_id] = {
                "cid": cid,
                "status": "success"
            }
            print(f"[{index}/{len(bv_list)}] BV: {bv_id}, CID: {cid}")
        except Exception as e:
            results[bv_id] = {
                "error": str(e),
                "status": "failed"
            }
            print(f"[{index}/{len(bv_list)}] BV: {bv_id}, Error: {str(e)}")

        if index < len(bv_list):
            time.sleep(1)

    with open('json/LLM_cid_list.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("\n结果已保存到 json/LLM_cid_list.json")
    print(
        f"成功: {sum(1 for v in results.values() if v['status'] == 'success')} 个")
    print(
        f"失败: {sum(1 for v in results.values() if v['status'] == 'failed')} 个")
