# 重构说明

技术栈没换：Selenium + requests + pandas + jieba + wordcloud。换的是代码怎么摊开。

## 原来什么样

| 位置 | 问题 |
| --- | --- |
| `bugs/`、`json/`、`cloud/` | 目录名按"作业第几步"起，跟代码职责没关系；`json/` 还和标准库同名 |
| 五个脚本 | 各自 `json.load` / `json.dump`，缩进 `2` 和 `4` 混用，编码写法也不统一 |
| 抓 BV / 查 cid / 拉弹幕 | 三份 requests/Selenium 调用各写一遍，头上都带着重复的 header 常量 |
| 停用词 | `deal_json.py` 和 `cloud.py` 各一份，内容还不一样（云的那份多过滤了"好/看/来/老师/学习"） |
| 逻辑与依赖 | 统计函数里直接 `jieba.lcut`，导表函数里直接 `pd.ExcelWriter`，不装全依赖就一行都跑不了 |
| 失败处理 | 大量 `except Exception: pass`，抓到一半断了只剩一句"失败" |

## 现在怎么分

```
cli.py          子命令编排（bvs / cids / danmaku / analyze / cloud / all）
  ├── crawler.py       Selenium 抓 BV、requests 查 cid
  ├── danmaku_api.py   拉弹幕、解压、风控异常
  ├── statistics.py    统计（分词器作为参数）
  ├── report.py        导出 Excel
  └── wordcloud_job.py 词云
        ↑
   parsing.py / storage.py / config.py   纯函数与路径
```

原来那五个脚本变成十几行的包装，仍然能 `python bugs/get_bv.py` 直接跑。

## 三个关键决定

**重依赖延迟导入。** `statistics.analyse(payload, tokenizer=...)` 的默认分词器才 import jieba；`report.write_excel` 才 import pandas；`crawler` 才 import selenium。结果是 27 个单测在只有标准库的机器上全绿。

**分词器做成参数。** 测试传 `lambda text: text.split(" ")`，就能断言"停用词被过滤、纯数字被过滤、词频累加正确"，不用等 jieba 分对了词。

**JSON 写临时文件再 replace。** 抓取是长流程，原来直接覆盖目标文件，中途断电会留下半个 JSON，下次 `json.load` 直接崩。现在先写 `.tmp` 再原子替换。

## 停用词合并

两份停用词取并集。影响：统计报表里"好、看、来、老师、学习、游戏"这类词不再出现。这是有意的——同一份数据做报表和做词云，过滤标准不该两套。

## 代价

- 目录层级变深，改一个逻辑要先找它在哪个模块。
- `json/` 这类历史目录名还在（数据文件都在里面），只是代码搬走了。
- 老入口脚本里有一段 `sys.path.insert`，看着不优雅，但能让"在仓库根目录直接跑脚本"这件事继续成立。
