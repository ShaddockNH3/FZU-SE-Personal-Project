import json
import os
import pandas as pd
import jieba
from collections import Counter, defaultdict

MODE_MAP = {
    '1': '普通滚动', '2': '普通滚动', '3': '普通滚动',
    '4': '底部弹幕', '5': '顶部弹幕', '6': '逆向弹幕',
    '7': '高级弹幕', '8': '代码弹幕', '9': 'BAS弹幕'
}

STOP_WORDS = set([
    # 基础中文停用词
    '的', '是', '了', '在', '也', '啊', '吗', '吧', '呢', '哦', '哈', '哈哈', '哈哈哈', '啊啊啊',
    '这', '那', '就', '都', '不', '我', '你', '他', '她', '它', '们', '个', '一', '有', '人', '个',
    '什么', '怎么', '为', '于', '上', '下', '左', '右', '前', '后', '里', '外', '都', '就', '还',
    '地', '得', '和', '与', '或', '被', '把', '但', '所以', '因为', '不过', '自己', '没有',
    '真的', '还是', '就是', '不是', '可以', '这个是', '为什么', '卧槽', '草', 'nb', 'respect',

    '\\', '-', '^', '_',
    '大', '很', '不错', '精彩', '讲', '又', '所有', '基本', '作用', '很大',
    'test', 'up', '三连', '万物', '之源', '逆行', '一号',

    'up主', 'UP主', 'UP', '阿婆主', '视频', '弹幕', '感谢', '主播', '直播', '直播间',
    '来了', '来了来了', '哈哈哈', '233', '2333', '666', '6666', '666666',

    '一个', '这个', '那个', '这里', '那里', '所以', '但是', '然而', '如果', '我们',
    '感觉', '觉得', '问题', '一样', '说', '看', '有', '没', '能', '做', '去', '想', '要',
    '一点', '一些', '一种', '一样', '有点', '东西', '为什么', '多少', '怎么', '这么',

    '，', '。', '！', '？', '：', '；', '（', '）', '[', ']', '【', '】', ' ',
    '.', '!', '?', '(', ')',
    '...', '....', '.....', '......', '→', '←', '…', '·', '《', '》',
    '~', '"', '"', '/', ',', ':', '"', '`', '*', '&', '%', '$', '#', '@',

    'this', 'is', 'a', 'to', 'and', 'the', 'that', 'of', 'for', 'in', 'it', 'with', 'on', 'was', 'as'
])


def get_mode_name(mode_str):
    return MODE_MAP.get(mode_str, f"未知类型({mode_str})")


def process_danmaku_data(input_filename='json/LLM_danmaku_realtime_save.json'):
    """读取JSON文件并统计弹幕数据"""

    mode_totals = Counter()
    mode_content_freq = defaultdict(Counter)
    mode_word_freq = defaultdict(Counter)

    print(f"正在打开文件 '{input_filename}'...")
    if not os.path.exists(input_filename):
        print(f"找不到文件 '{input_filename}'！")
        return None, None, None

    with open(input_filename, 'r', encoding='utf-8') as f:
        all_data = json.load(f)

    print("文件已打开，正在分词处理...")

    total_danmaku_processed = 0

    for bv, video_data in all_data.items():
        if video_data.get('danmaku_list') and video_data.get(
                'status') != 'fetch_failed_or_no_danmaku':
            for danmaku in video_data['danmaku_list']:
                try:
                    attributes = danmaku.get('attributes')
                    content = danmaku.get('content')

                    if not attributes or content is None:
                        continue

                    mode = attributes.split(',')[1]

                    mode_totals[mode] += 1

                    mode_content_freq[mode][content] += 1

                    word_list = jieba.lcut(str(content).lower())

                    filtered_words = []
                    for word in word_list:
                        word = word.strip()

                        if not word:
                            continue
                        if word in STOP_WORDS:
                            continue
                        if word.isnumeric():
                            continue

                        filtered_words.append(word)

                    mode_word_freq[mode].update(filtered_words)
                    total_danmaku_processed += 1

                except Exception as e:
                    print(f"  > 处理弹幕时出错 (BV: {bv}): {e}，跳过: {danmaku}")

    print(f"处理完毕！总共处理了 {total_danmaku_processed} 条弹幕！")
    return mode_totals, mode_content_freq, mode_word_freq


def write_to_excel(
        mode_totals,
        mode_content_freq,
        mode_word_freq,
        output_filename='xlsx/LLM_danmaku_statistics.xlsx'):
    """将统计数据写入Excel文件"""
    if not mode_totals:
        print("没有任何数据可以写入 Excel。")
        return

    print(f"正在准备写入 Excel 文件: {output_filename} ...")

    try:
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:

            totals_data_list = []
            for mode, count in mode_totals.items():
                totals_data_list.append({
                    '弹幕类型ID': mode, '类型名称': get_mode_name(mode), '总数量': count
                })
            df_totals = pd.DataFrame(totals_data_list).sort_values(
                by='总数量', ascending=False)
            df_totals.to_excel(writer, sheet_name='弹幕类型总览', index=False)

            top_sentence_list = []
            for mode, content_counter in mode_content_freq.items():
                type_name = get_mode_name(mode)
                rank = 1
                for content, freq in content_counter.most_common(8):
                    top_sentence_list.append({
                        '弹幕类型ID': mode, '类型名称': type_name, '排名': rank,
                        '弹幕内容(整句)': content, '出现次数': freq
                    })
                    rank += 1
            df_top_sentences = pd.DataFrame(top_sentence_list)
            df_top_sentences.to_excel(
                writer, sheet_name='热门弹幕(整句)Top8', index=False)

            top_word_list = []
            for mode, word_counter in mode_word_freq.items():
                type_name = get_mode_name(mode)
                rank = 1
                for word, freq in word_counter.most_common(8):
                    top_word_list.append({
                        '弹幕类型ID': mode, '类型名称': type_name, '排名': rank,
                        '高频词(分词)': word, '出现次数': freq
                    })
                    rank += 1
            df_top_words = pd.DataFrame(top_word_list)
            df_top_words.to_excel(
                writer, sheet_name='热门词频(分词)Top8', index=False)

        print(f"成功生成 Excel 报告 '{output_filename}'！")

    except Exception as e:
        print(f"写入 Excel 失败。错误信息: {e}")
        print("请检查是否已安装 'openpyxl' 和 'jieba' 库。")


if __name__ == "__main__":
    print("程序开始运行...")
    totals, freq_sentence, freq_word = process_danmaku_data(
        input_filename='json/LLM_danmaku_realtime_save.json')

    if totals:
        write_to_excel(
            totals,
            freq_sentence,
            freq_word,
            output_filename='xlsx/LLM_danmaku_statistics.xlsx')
    else:
        print("没有可以分析的数据。")
