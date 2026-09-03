# 实验一：清华园音乐档案馆

## 一、系统概述

本系统以网易云音乐公开歌曲与歌手信息为基础，使用 Django 和 SQLite 构建音乐信息检索网站。系统提供歌曲索引、人物档案、详情查看、子串搜索及评论功能，页面采用“清华园·人文校园”设计语言：清华紫、米白纸张色、档案编号、留白网格和唱片卡片共同构成视觉识别。

## 二、数据与爬虫

爬虫通过网易云音乐公开接口读取歌单和歌曲元数据，不下载音视频。程序设置 User-Agent、请求间隔、超时、缓存目录和异常提示；歌曲保存名称、歌手、歌词、封面和原始链接，歌手保存名称、图片、简介和原始链接。`crawl_netease` 命令支持歌单 ID、数量限制、请求间隔和缓存路径。

## 三、主要功能

首页为歌曲分页索引；歌手页为人物分页索引。歌曲详情展示封面、歌词、歌手链接和网易云原始链接，并支持评论新增、倒序显示和删除。搜索可选择歌曲或歌手，显示结果数量及后端耗时。所有页面共享导航、搜索、分页、档案卡片和响应式样式。

## 四、数据分析结论

运行 `python manage.py seed_archive` 或导入网易云数据后执行 `python analysis/analyze_data.py`，即可复现以下分析：

1. 统计歌曲总量、歌手总量和平均作品数，说明样本覆盖规模。
2. 对歌手作品数排序，找出作品数量最多的歌手，并绘制前十名柱状图。
3. 统计歌词长度的平均值和中位数，观察样本歌曲的文本规模。

## 五、运行方式

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_archive
python manage.py runserver
```

网易云爬取示例：

```bash
python manage.py crawl_netease 3778678 --limit 100 --delay 1.5
```
