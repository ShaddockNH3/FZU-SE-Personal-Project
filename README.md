# FZU-SE-Personal-Project

福州大学 2025 软件工程个人编程作业：抓 B 站弹幕、统计弹幕类型与高频词、导出 Excel、出词云。纯 Python，Selenium 抓页、requests 取数据、pandas 导表、jieba 分词。

## 快速开始

```bash
pip install -r requirements.txt

python -m bili bvs        # 按关键词抓 BV 号
python -m bili cids       # 查 cid
python -m bili danmaku    # 拉弹幕，断点续跑
python -m bili analyze    # 统计并导出 xlsx
python -m bili cloud      # 出词云
python -m bili all        # 从第一步跑到底
```

老入口也还能用，行为和以前一致：

```bash
python bugs/get_bv.py
python bugs/get_cid.py
python bugs/get_danmaku.py
python json/deal_json.py
python cloud/cloud.py
```

抓 BV 号要本机有 Chrome（Selenium + webdriver-manager 自动配驱动）。弹幕接口有风控，每两个视频之间随机等 10~20 秒，撞 412 会退避 120 秒。

## 命令与产物

| 命令 | 读取 | 产出 |
| --- | --- | --- |
| `bvs` | 关键词 | `json/LLM_bv_list.json` |
| `cids` | BV 列表 | `json/LLM_cid_list.json`（含每个视频的成败） |
| `danmaku` | cid 列表 | `json/LLM_danmaku_realtime_save.json`（边抓边存） |
| `analyze` | 弹幕存档 | `xlsx/LLM_danmaku_statistics.xlsx`（三个 sheet） |
| `cloud` | 弹幕存档 | `cloud/LLM_danmaku_wordcloud_beautiful.png` |

关键词、目标数量、路径、节流参数都在 `bili/config.py`。

## 项目结构

```
bili/
├── config.py        关键词、路径、接口、弹幕类型表、停用词
├── parsing.py       BV/cid 正则、弹幕 XML 解析（纯函数）
├── statistics.py    类型计数、整句排行、词频排行（分词器可注入）
├── report.py        导出 Excel（pandas 延迟导入）
├── crawler.py       Selenium 抓 BV、requests 查 cid
├── danmaku_api.py   拉弹幕、raw-deflate 解压、风控异常
├── wordcloud_job.py 词云渲染
└── cli.py           子命令
bugs/ json/ cloud/   原来的入口脚本，现在各十几行
docs/                作业要求、PSP 表、代码质量与测试报告
```

重依赖都在函数内部 import，所以解析与统计的单测不需要装 selenium / pandas / jieba。

## 测试

```bash
python -m unittest discover -s tests -t .
```

27 个用例：BV/cid 提取、弹幕 XML 解析、类型与词频统计（注入假分词器）、Excel 行构造、JSON 读写（含坏文件与临时文件清理）。

## 已知问题

- 停用词把 `json/deal_json.py` 和 `cloud/cloud.py` 两份合成了一份（并集），词云和报表的过滤标准现在一致，但和旧报表的数字会有细微差别。
- 抓取依赖 B 站页面结构，改版就要重新对 XPATH。
- 弹幕接口按 cid 逐个拉，没有并发；360 个视频按节流跑要一个多小时。
- `requirements.txt` 原来是 UTF-16，`pip install -r` 在某些环境会报编码错，已改 UTF-8。
- 字体是硬编码的几个常见路径，Linux 上没装中文字体时词云会是方块。

## 更多

数据格式与重构说明见 [docs/DESIGN.md](docs/DESIGN.md)。

## 致谢

[jieba](https://github.com/fxsjy/jieba)、[wordcloud](https://github.com/amueller/word_cloud)、[Selenium](https://www.selenium.dev/)、[pandas](https://pandas.pydata.org/)。

## License

MIT，见 [LICENSE](LICENSE)。
