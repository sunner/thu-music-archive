"""生成实验报告所需的三个可复现统计结论。"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'music_archive.settings')
import django
django.setup()
from collections import Counter
from archive.models import Song

OUT = Path('analysis/output'); OUT.mkdir(parents=True, exist_ok=True)
songs = list(Song.objects.select_related('artist'))
counts = Counter(song.artist.name for song in songs)
lyrics = [len(song.lyrics) for song in songs]
print(f'结论1：样本共 {len(songs)} 首歌曲、{len(counts)} 位歌手，平均每位歌手 {len(songs)/len(counts):.2f} 首。')
print(f'结论2：作品数量最多的歌手是 {counts.most_common(1)[0][0]}，共有 {counts.most_common(1)[0][1]} 首。')
print(f'结论3：歌词文本平均 {sum(lyrics)/len(lyrics):.1f} 字符，中位数 {sorted(lyrics)[len(lyrics)//2]} 字符。')
try:
    import matplotlib.pyplot as plt
    top = counts.most_common(10)
    plt.figure(figsize=(10, 5)); plt.bar([x[0] for x in top], [x[1] for x in top], color='#4b1f5b'); plt.xticks(rotation=35, ha='right'); plt.ylabel('歌曲数量'); plt.title('作品数量最多的十位歌手'); plt.tight_layout(); plt.savefig(OUT / 'top_artists.png', dpi=160); plt.close()
except ImportError:
    print('未安装 matplotlib，跳过图表生成。')
