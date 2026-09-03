# 清华园音乐档案馆

## 快速运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_archive
python manage.py runserver
```

访问 http://127.0.0.1:8000/。项目包含歌曲/歌手档案、分页、子串搜索、评论增删和清华园人文校园风界面。
