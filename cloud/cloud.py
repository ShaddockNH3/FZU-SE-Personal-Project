import json
import os
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

STOP_WORDS = set([
    # 基础中文停用词
    '的', '是', '了', '在', '也', '啊', '吗', '吧', '呢', '哦', '哈', '哈哈', '哈哈哈', '啊啊啊',
    '这', '那', '就', '都', '不', '我', '你', '他', '她', '它', '们', '个', '一', '有', '人', '个',
    '什么', '怎么', '为', '于', '上', '下', '左', '右', '前', '后', '里', '外', '都', '就', '还',
    '地', '得', '和', '与', '或', '被', '把', '但', '所以', '因为', '不过', '自己', '没有',
    '真的', '还是', '就是', '不是', '可以', '这个是', '为什么', '卧槽', '草', 'nb', 'respect', '多',

    '\\', '-', '^', '_', '~', '"', '"', '/', ',', ':', '"', '`',
    '这个', '一个', '好', '看', '来', '开始', '现在', '收藏', '老师', '学习', '游戏',
    '大', '很', '不错', '精彩', '讲', '又', '所有', '基本', '作用', '很大',
    'test', 'up', '三连', '万物', '之源', '逆行', '一号',

    'up主', 'UP主', 'UP', '阿婆主', '视频', '弹幕', '感谢', '主播', '直播', '直播间',
    '来了', '来了来了', '哈哈哈', '233', '2333', '666', '6666', '666666',

    '感觉', '觉得', '问题', '一样', '说', '看', '有', '没', '能', '做', '去', '想', '要',
    '一点', '一些', '一种', '一样', '有点', '东西', '为什么', '多少', '怎么', '这么',

    '，', '。', '！', '？', '：', '；', '（', '）', '[', ']', '【', '】', ' ',
    '.', '!', '?', '(', ')',
    '...', '....', '.....', '......', '→', '←', '…', '·', '《', '》',
    '*', '&', '%', '$', '#', '@',

    'this', 'is', 'a', 'to', 'and', 'the', 'that', 'of', 'for', 'in', 'it', 'with', 'on', 'was', 'as'
])


def create_word_cloud(input_filename='json/LLM_danmaku_realtime_save.json',
                      output_filename='LLM_danmaku_wordcloud_beautiful.png',
                      mask_image_path='mask.png'):
    """读取弹幕并生成词云图"""
    print(f"正在打开弹幕文件 '{input_filename}'...")
    if not os.path.exists(input_filename):
        print(f"找不到文件 '{input_filename}'！")
        return

    with open(input_filename, 'r', encoding='utf-8') as f:
        all_data = json.load(f)

    print("文件打开成功，正在收集所有弹幕文字...")

    all_text = ""
    for bv, video_data in all_data.items():
        if video_data.get('danmaku_list') and video_data.get(
                'status') != 'fetch_failed_or_no_danmaku':
            for danmaku in video_data['danmaku_list']:
                if danmaku and danmaku.get('content'):
                    all_text += " " + danmaku['content']

    if not all_text:
        print("文件中没有弹幕内容，无法制作词云图。")
        return

    print("文字收集完毕！正在使用分词工具进行分词和过滤...")
    word_list = jieba.lcut(all_text.lower())

    filtered_words = [word.strip() for word in word_list if word.strip(
    ) and word.strip() not in STOP_WORDS and not word.isnumeric()]

    final_text = " ".join(filtered_words)

    print("过滤完成，开始准备形状和颜色...")
    try:
        mask_array = np.array(Image.open(mask_image_path))
        print(f"成功加载形状图片 '{mask_image_path}'！")
    except FileNotFoundError:
        print(f"找不到形状图片 '{mask_image_path}'！将生成一个普通的方形词云。")
        mask_array = None

    print("开始绘制词云图，请稍等片刻...")

    font_path = 'C:/Windows/Fonts/simhei.ttf'

    try:
        wordcloud = WordCloud(
            font_path=font_path,
            width=1600,
            height=900,
            background_color="white",
            mask=mask_array,
            max_words=300,
            colormap='viridis',
            contour_width=1,
            contour_color='steelblue',
            collocations=False
        ).generate(final_text)

        print("词云图生成成功！正在保存...")

        plt.figure(figsize=(20, 10), facecolor='white')
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.tight_layout(pad=0)

        plt.savefig(output_filename, dpi=300)

        print(f"词云图 '{output_filename}' 已经保存成功！")

    except FileNotFoundError:
        print(f"找不到字体文件 '{font_path}'！请检查路径或更换字体。")
    except Exception as e:
        print(f"生成词云时发生错误: {e}")


if __name__ == "__main__":
    create_word_cloud(
        input_filename='json/LLM_danmaku_realtime_save.json',
        output_filename='LLM_danmaku_wordcloud_beautiful.png',
        mask_image_path='mask.png'
    )
