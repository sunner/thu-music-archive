"""网易云音乐公开接口的数据适配器。仅读取歌曲/歌手信息，不下载音视频。"""
import time
from typing import Any
import requests

API = 'https://music.163.com/api'

class NeteaseClient:
    def __init__(self, delay: float = 1.0):
        self.delay = max(delay, 0.2)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'MusicArchiveStudentCrawler/1.0'})

    def playlist(self, playlist_id: int, limit: int = 100) -> list[dict[str, Any]]:
        """读取歌单中的歌曲元数据，并按请求间隔访问网易云。"""
        response = self.session.get(f'{API}/playlist/detail', params={'id': playlist_id}, timeout=20)
        response.raise_for_status()
        tracks = response.json().get('playlist', {}).get('trackIds', [])[:limit]
        songs = []
        for start in range(0, len(tracks), 100):
            ids = ','.join(str(item['id']) for item in tracks[start:start + 100])
            time.sleep(self.delay)
            detail = self.session.get(f'{API}/song/detail', params={'ids': f'[{ids}]'}, timeout=20)
            detail.raise_for_status()
            for raw in detail.json().get('songs', []):
                artists = raw.get('ar') or raw.get('artists') or []
                artist = artists[0] if artists else {}
                songs.append({'title': raw.get('name', '未命名歌曲'), 'artist': artist.get('name', '未知歌手'), 'artist_id': artist.get('id'), 'image_url': raw.get('al', {}).get('picUrl', ''), 'source_url': f'https://music.163.com/#/song?id={raw.get("id")}', 'lyrics': ''})
        return songs
