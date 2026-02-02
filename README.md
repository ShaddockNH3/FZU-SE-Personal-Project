# FZU-SE-Personal-Project

福州大学2025年下半学期软件工程个人编程作业

## 项目简介

本项目实现了B站视频弹幕的爬取、分析和可视化功能。

## 运行顺序

### 1. 环境准备

```bash
pip install -r requirements.txt
```

### 2. 数据爬取（按顺序执行）

```bash
# 步骤1: 爬取BV号
python bugs/get_bv.py

# 步骤2: 获取CID
python bugs/get_cid.py

# 步骤3: 爬取弹幕数据
python bugs/get_danmaku.py
```

### 3. 数据分析

```bash
# 生成统计报表
python json/deal_json.py

# 生成词云图
python cloud/cloud.py
```

## 项目结构

```
├── bugs/              # 爬虫模块
│   ├── get_bv.py      # 爬取视频BV号
│   ├── get_cid.py     # 获取视频CID
│   └── get_danmaku.py # 爬取弹幕数据
├── json/              # 数据存储
│   ├── deal_json.py   # 弹幕统计分析
│   ├── LLM_bv_list.json
│   ├── LLM_cid_list.json
│   └── LLM_danmaku_realtime_save.json
├── xlsx/              # 输出文件
│   └── LLM_danmaku_statistics.xlsx
├── cloud/             # 可视化
│   └── cloud.py       # 词云生成
├── docs/              # 项目文档
│   ├── 0.作业要求文档.md
│   ├── 1.PSP表格.md
│   ├── 2.我的观点.md
│   ├── 3.代码质量分析报告.md
│   ├── 4.性能分析报告.md
│   └── 5.单元测试报告.md
└── tests/             # 单元测试
```

## 输出说明

- **json/LLM_bv_list.json**: BV号列表
- **json/LLM_cid_list.json**: CID列表
- **json/LLM_danmaku_realtime_save.json**: 弹幕原始数据
- **xlsx/LLM_danmaku_statistics.xlsx**: 弹幕统计表格
- **LLM_danmaku_wordcloud_beautiful.png**: 弹幕词云图

## 文档

详细的项目文档请查看 `docs/` 目录：
- 0.作业要求文档
- 1.PSP表格
- 2.我的观点
- 3.代码质量分析报告
- 4.性能分析报告
- 5.单元测试报告

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**ShaddockNH3** - [GitHub](https://github.com/ShaddockNH3)

Student ID: 022302217
